import os
import requests
from tqdm import tqdm
from acdh_cidoc_pyutils import (
    make_e42_identifiers,
    make_appellations,
    make_birth_death_entities,
    make_affiliations,
    make_entity_label,
    make_occupations,
)
from acdh_xml_pyutils.xml import NSMAP
from acdh_cidoc_pyutils.namespaces import CIDOC
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import get_xmlid
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF


g = Graph()
domain = "https://amp.acdh.oeaw.ac.at/"
PU = Namespace(domain)

if os.environ.get("NO_LIMIT"):
    LIMIT = False
    print("no limit")
else:
    LIMIT = False

rdf_dir = "./datasets"
os.makedirs(rdf_dir, exist_ok=True)

index_file = "./listperson.xml"
entity_type = "person"

print("check if source file exists")
BASE_URL = "https://raw.githubusercontent.com/Auden-Musulin-Papers/amp-entities/refs/heads/main/out/"  # noqa
if os.path.exists(index_file):
    pass
else:
    url = f"{BASE_URL}amp-index-persons.xml"
    print(f"fetching {index_file} from {url}")
    response = requests.get(url)
    with open(index_file, "wb") as file:
        file.write(response.content)


doc = TeiReader(index_file)
items = doc.any_xpath(f".//tei:{entity_type}[@xml:id]")
if LIMIT:
    items = items[:LIMIT]

for x in tqdm(items, total=len(items)):
    xml_id = get_xmlid(x)
    item_label = make_entity_label(x.xpath(".//tei:persName[1]", namespaces=NSMAP)[0])[
        0
    ]
    item_id = f"{PU}{xml_id}"
    subj = URIRef(item_id)
    g.add((subj, RDF.type, CIDOC["E21_Person"]))
    affilliations = make_affiliations(
        subj,
        x,
        f"{PU}org__",
        item_label,
        org_id_xpath="./tei:orgName/@key",
        org_label_xpath="./tei:orgName/text()",
    )
    g += affilliations

    # ids
    g += make_e42_identifiers(
        subj,
        x,
        type_domain="https://pfp-custom-types",
        default_lang="de",
    )

    # names
    g += make_appellations(
        subj, x, type_domain="https://pfp-custom-types", default_lang="de"
    )

    # birth
    event_graph, birth_uri, birth_timestamp = make_birth_death_entities(
        subj,
        x,
        f"{PU}place__",
        event_type="birth",
        verbose=True,
        default_prefix="Geburt von",
        date_node_xpath="/tei:date[1]",
        place_id_xpath="//tei:settlement[1]/@key",
    )
    try:
        g.add((subj, CIDOC["P98i_was_born"], birth_uri))
    except AssertionError:
        pass
    g += event_graph

    # death
    event_graph, death_uri, birth_timestamp = make_birth_death_entities(
        subj,
        x,
        f"{PU}place__",
        event_type="death",
        verbose=True,
        default_prefix="Tod von",
        date_node_xpath="/tei:date[1]",
        place_id_xpath="//tei:settlement[1]/@key",
    )
    try:
        g.add((subj, CIDOC["P100i_died_in"], death_uri))
    except AssertionError:
        pass
    g += event_graph

    # occupations
    g += make_occupations(subj, x, id_xpath="./@key")[0]

save_path = os.path.join(rdf_dir, f"amp_{entity_type}.ttl")
print(f"saving graph as {save_path}")
g.serialize(save_path)
