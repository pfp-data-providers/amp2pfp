import os
from rdflib import Graph, URIRef, RDFS, Literal


out_file = os.path.join("scripts", "types.ttl")
g = Graph()
id_types = [
    "https://pfp-custom-types/idno/URI/GEONAMES",
    "https://pfp-custom-types/idno/URI/WIKIDATA",
    "https://pfp-custom-types/idno/URI/PMB",
    "https://pfp-custom-types/idno/URI/GND",
    "https://pfp-custom-types/idno/xml-id",
]
appellation_types = [
    "https://pfp-custom-types/person/persname",
    "https://pfp-custom-types/org/orgname",
    "https://pfp-custom-types/place/placename",
]
for x in appellation_types:
    g.add((URIRef(x), RDFS.label, Literal("appellation type", lang="en")))
for x in id_types:
    g.add((URIRef(x), RDFS.label, Literal("identifier type", lang="en")))
g.serialize(out_file)
print(f"Written to {out_file}")
