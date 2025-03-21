from acdh_cidoc_pyutils import CIDOC

EVENT_PATTERNS = {
    "birth": {
        "type": CIDOC["E67_Birth"],
        "subject_predicate": CIDOC["P98_brought_into_life"],
        "object_predicate": CIDOC["P7_took_place_at"],
        "time_predicate": CIDOC["P4_has_time-span"],
        "template": {
            "object": "{subject} wurde geboren in {object}",
            "time": "{subject} wurde geboren am {date}",
        },
    },
    "death": {
        "type": CIDOC["E69_Death"],
        "subject_predicate": CIDOC["P100_was_death_of"],
        "object_predicate": CIDOC["P7_took_place_at"],
        "time_predicate": CIDOC["P4_has_time-span"],
        "template": {
            "object": "{subject} starb in {object}",
            "time": "{subject} starb am {date}",
        },
    },
}
