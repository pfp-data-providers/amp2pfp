from rdflib import Graph
from config import EVENT_PATTERNS
from utils import extract_event_info


g = Graph()
g.parse("verbalize_graph/out/verbalized.nt")

items = []
for event_type, config in EVENT_PATTERNS.items():
    for x in extract_event_info(g, config):
        print(x)
