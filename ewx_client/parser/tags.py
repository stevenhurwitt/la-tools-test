import json

from energyworx_client.parser import generic_payload_parser

def parse_tags(result):
    rows = result['rows']
    metadata = result['metadata']['fields']
    try:
        return generic_payload_parser(json.loads(rows), metadata)
    except KeyError:
        return result