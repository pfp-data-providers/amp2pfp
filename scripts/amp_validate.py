from rdflib import Graph
from pyshacl import validate

# Load the SHACL shapes graph from the URL
shacl_url = "https://pfp-schema.acdh-ch-dev.oeaw.ac.at/shacl/shacl.ttl"
shacl_graph = Graph()
shacl_graph.parse(shacl_url, format="turtle")

# Load the data graph from the local file
data_graph = Graph()
data_graph.parse("datasets/amp.ttl", format="turtle")

# Perform SHACL validation
conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shacl_graph,
    inference="rdfs",
    abort_on_first=False,
    meta_shacl=False,
    advanced=True,
    debug=False,
)

# Print validation results
validation_report = "validation_report.txt"
with open(validation_report, "w", encoding="utf-8") as fp:
    fp.write(results_text)

print(f"The graph conforms: {conforms}; see {validation_report}")
