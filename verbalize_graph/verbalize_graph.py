import json
import glob
import os
import shutil
from rdflib import Graph, Literal, URIRef, RDF, RDFS

g = Graph()
out_file = "verbalized"
ontology_folder = os.path.join("verbalize_graph", "ontologies")
output_folder = os.path.join("verbalize_graph", "out")
shutil.rmtree(output_folder, ignore_errors=True)
os.mkdir(output_folder)

ontologies = glob.glob(f"{ontology_folder}/*.ttl")
for x in ontologies:
    g.parse(x)

for s, p, o in g.triples((None, None, None)):
    if isinstance(o, Literal) and o.language and o.language not in ["de", "en", "und"]:
        g.remove((s, p, o))
g.parse("./datasets/amp.nt")

subjects = {}
predicates = {}
objects = {}

# Process subjects
for s in set(g.subjects()):
    subjects[str(s)] = {"label": [], "class_uri": [], "class_label": []}
    # get labels
    for label in g.objects(s, RDFS.label):
        label_dict = {
            "label": str(label),
            "lang": (
                label.language
                if isinstance(label, Literal) and label.language
                else "und"
            ),
        }
        subjects[str(s)]["label"].append(label_dict)

    if not subjects[str(s)]["label"]:
        subjects[str(s)]["label"].append({"label": "no label provided", "lang": "und"})

    # get classes and their labels
    for class_uri in g.objects(s, RDF.type):
        subjects[str(s)]["class_uri"].append(str(class_uri))
        # get class labels
        for class_label in g.objects(class_uri, RDFS.label):
            label_dict = {
                "label": str(class_label),
                "lang": (
                    class_label.language
                    if isinstance(class_label, Literal) and class_label.language
                    else "und"
                ),
            }
            subjects[str(s)]["class_label"].append(label_dict)

# Process predicates
for p in set(g.predicates()):
    predicates[str(p)] = {"label": [], "class_uri": [], "class_label": []}
    # get labels
    for label in g.objects(p, RDFS.label):
        label_dict = {
            "label": str(label),
            "lang": (
                label.language
                if isinstance(label, Literal) and label.language
                else "und"
            ),
        }
        predicates[str(p)]["label"].append(label_dict)

    if not predicates[str(p)]["label"]:
        predicates[str(p)]["label"].append({"label": str(p), "lang": "und"})

    # get classes and their labels
    for class_uri in g.objects(p, RDF.type):
        predicates[str(p)]["class_uri"].append(str(class_uri))
        # get class labels
        for class_label in g.objects(class_uri, RDFS.label):
            label_dict = {
                "label": str(class_label),
                "lang": (
                    class_label.language
                    if isinstance(class_label, Literal) and class_label.language
                    else "und"
                ),
            }
            predicates[str(p)]["class_label"].append(label_dict)

# Process objects
for o in set(g.objects()):
    if isinstance(o, Literal):
        objects[str(o)] = {
            "value": str(o),
            "lang": (
                o.language if o.language else "und" if isinstance(o, Literal) else None
            ),
            "datatype": str(o.datatype) if o.datatype else None,
        }
    elif isinstance(o, URIRef):
        objects[str(o)] = {"value": None, "lang": None, "datatype": None}
        # Get label for URI
        for label in g.objects(o, RDFS.label):
            objects[str(o)]["value"] = str(label)
            objects[str(o)]["lang"] = (
                label.language
                if isinstance(label, Literal) and label.language
                else "und"
            )
            break
        # If no label found, use URI as value
        if objects[str(o)]["value"] is None:
            objects[str(o)]["value"] = str(o)
            objects[str(o)]["lang"] = "und"

g.serialize(
    os.path.join(output_folder, f"{out_file}.nt"), format="nt", encoding="utf-8"
)
g.serialize(os.path.join(output_folder, f"{out_file}.ttl"))

# Save all dictionaries to JSON
with open(os.path.join(output_folder, f"{out_file}.json"), "w", encoding="utf-8") as fp:
    json.dump(
        {"subjects": subjects, "predicates": predicates, "objects": objects},
        fp,
        ensure_ascii=False,
        indent=2,
    )

# Create triples with labels
seen_uris = set()  # Track URIs we've already seen
with open(os.path.join(output_folder, f"{out_file}.txt"), "w", encoding="utf-8") as f:
    current_subject = None
    current_predicate = None
    for s, p, o in g:
        s_str = str(s)
        p_str = str(p)
        o_str = str(o)

        # Get subject label (prefer German)
        s_label = "no label"
        if s_str in subjects and subjects[s_str]["label"]:
            de_labels = [label_item for label_item in subjects[s_str]["label"] if label_item["lang"] == "de"]
            if de_labels:
                s_label = de_labels[0]["label"]
            else:
                s_label = subjects[s_str]["label"][0]["label"]

        # Write subject URI info when subject changes and hasn't been seen before
        if s_str not in seen_uris:
            seen_uris.add(s_str)
            f.write(f"Die Graph-URI für {s_label} ist {s_str}.\n")
            current_subject = s_str

        # Get predicate label (prefer German)
        p_label = str(p)
        if p == RDF.type:
            p_label = "is a"
        elif p == RDFS.label:
            p_label = "hat als Label"
        elif p_str in predicates and predicates[p_str]["label"]:
            de_labels = [label_item for label_item in predicates[p_str]["label"] if label_item["lang"] == "de"]
            if de_labels:
                p_label = de_labels[0]["label"]
            else:
                p_label = predicates[p_str]["label"][0]["label"]

        # Write predicate URI info when predicate changes and hasn't been seen before
        if p_str not in seen_uris:
            seen_uris.add(p_str)
            f.write(f"Die Graph-URI für {p_label} ist {p_str}.\n")
            current_predicate = p_str

        # Get object label (prefer German)
        o_label = "no label"
        if o_str in objects:
            if isinstance(o, URIRef):
                if objects[o_str]["lang"] == "de":
                    o_label = objects[o_str]["value"]
                else:
                    o_label = objects[o_str]["value"]
            else:
                o_label = objects[o_str]["value"]

        # Write triple labels to file
        triple_str = f"{s_label} {p_label} {o_label}\n"
        f.write(triple_str)
