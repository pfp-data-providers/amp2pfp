from rdflib import Graph, RDFS, RDF


def extract_event_info(g: Graph, event_config: dict) -> list[str]:
    """Extract information about events based on configuration."""
    results = []
    events = g.subjects(RDF.type, object=event_config["type"])

    for event in events:
        # Get subject info
        subject = g.value(subject=event, predicate=event_config["subject_predicate"])
        subject_label = g.value(subject=subject, predicate=RDFS.label)

        # Get object info
        object_ = g.value(subject=event, predicate=event_config["object_predicate"])
        object_label = g.value(subject=object_, predicate=RDFS.label)

        # Get time info
        time_span = g.value(subject=event, predicate=event_config["time_predicate"])
        date_label = g.value(subject=time_span, predicate=RDFS.label)

        # Create result strings using templates
        if object_label:
            results.append(
                event_config["template"]["object"].format(
                    subject=subject_label, object=object_label
                )
            )
        if date_label:
            results.append(
                event_config["template"]["time"].format(
                    subject=subject_label, date=date_label
                )
            )

    return results
