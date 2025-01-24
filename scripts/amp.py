import glob
import os
from rdflib import Graph

prefix = "amp"
type_file = os.path.join("scripts", "types.ttl")

files = glob.glob(f"./datasets/{prefix}_*.ttl")

if len(files) != 3:
    print("there is a least on file missing! Stopping script")
else:
    out_file = os.path.join("datasets", f"{prefix}.ttl")
    g = Graph()
    g.bind("geo", "http://www.opengis.net/ont/geosparql#")
    for x in files:
        g.parse(x)
        os.unlink(x)
    g.parse(type_file)
    print(f"serializing graph to {out_file}")
    g.serialize(out_file)
