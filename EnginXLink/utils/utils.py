import json


def pretty_print_json(document):
    return json.dumps(document, sort_keys=True, indent=4, separators=(',', ': '))