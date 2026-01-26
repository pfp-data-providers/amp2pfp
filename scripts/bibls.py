import os

import requests
from acdh_cidoc_pyutils import (
    make_appellations,
    make_e42_identifiers,
)
from acdh_cidoc_pyutils.namespaces import CIDOC, SARI_FRBROO
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import check_for_hash, extract_fulltext, get_xmlid
from acdh_xml_pyutils.xml import NSMAP
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS
from tqdm import tqdm

TYPE_DOMAIN = "https://pfp-custom-types"

g = Graph()
g.parse(
    "https://pfp-schema.acdh.oeaw.ac.at/types/person-work-publication/person-work-publication.ttl"
)
domain = "https://amp.acdh.oeaw.ac.at/"
PU = Namespace(domain)
LRMOO = Namespace("http://iflastandards.info/ns/lrm/lrmoo/")

rdf_dir = "./datasets"
os.makedirs(rdf_dir, exist_ok=True)

entity_type = "bibl"
index_file = f"list{entity_type}.xml"

author_type = URIRef(
    "https://pfp-schema.acdh.oeaw.ac.at/types/person-work-publication/#Creator"
)
author_type_label = g.value(author_type, RDFS.label)
g.add((author_type, RDF.type, CIDOC["E55_Type"]))


print("check if source file exists")
BASE_URL = "https://raw.githubusercontent.com/Auden-Musulin-Papers/amp-entities/refs/heads/main/out/amp-index-works.xml"  # noqa
if os.path.exists(index_file):
    pass
else:
    url = BASE_URL
    print(f"fetching {index_file} from {url}")
    response = requests.get(url)
    with open(index_file, "wb") as file:
        file.write(response.content)

doc = TeiReader(index_file)
items = doc.any_xpath(f".//tei:{entity_type}[@xml:id]")

for x in tqdm(items, total=len(items)):
    xml_id = get_xmlid(x)
    item_id = f"{PU}{xml_id}"
    subj = URIRef(item_id)
    g.add((subj, RDF.type, LRMOO["F3_Manifestation"]))

    # ids
    g += make_e42_identifiers(
        subj,
        x,
        type_domain=TYPE_DOMAIN,
        default_lang="de",
    )

    # names
    g += make_appellations(subj, x, type_domain=TYPE_DOMAIN, default_lang="en")

    authors = x.xpath("./tei:author[@ref]", namespaces=NSMAP)
    if authors:
        publication_event_uri = URIRef(f"{subj}/F30")
        g.add((publication_event_uri, SARI_FRBROO["R24_created"], subj))
        g.add((publication_event_uri, RDF.type, LRMOO["F30_Manifestation_Creation"]))
        label = g.value(subj, RDFS.label)
        g.add(
            (
                publication_event_uri,
                RDFS.label,
                Literal(f"Publication of: {label}", lang="en"),
            )
        )
        g.add((subj, LRMOO["R24i_was_created_through"], publication_event_uri))
        g.add((publication_event_uri, LRMOO["R24_created"], subj))
        for x in authors:
            author_ref = check_for_hash(x.attrib["ref"])
            author_label = extract_fulltext(x)
            author_uri = URIRef(f"{PU}{author_ref}")
            carried_out_uri = URIRef(f"{publication_event_uri}/PC14/{author_ref}")
            g.add((carried_out_uri, RDF.type, CIDOC["PC14_carried_out_by"]))
            g.add((publication_event_uri, CIDOC["P01i_is_domain_of"], carried_out_uri))
            g.add((carried_out_uri, CIDOC["P01_has_domain"], publication_event_uri))
            g.add((carried_out_uri, CIDOC["P02_has_range"], author_uri))
            g.add((carried_out_uri, CIDOC["P14.1_in_the_role_of"], author_type))
            g.add(
                (
                    carried_out_uri,
                    RDFS.label,
                    Literal(f"{author_label} -> {author_type_label} -> {label}"),
                )
            )

save_path = os.path.join(rdf_dir, f"amp_{entity_type}.nt")
print(f"saving graph as {save_path}")
g.serialize(save_path, format="nt", encoding="utf-8")
