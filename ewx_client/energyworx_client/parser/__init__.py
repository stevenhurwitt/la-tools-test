import logging


def generic_payload_parser(rows, metadata, target_object=None):
    """ Parses a BigQuery output

    Args:
        rows:
        metadata:
        target_object:

    Returns:
        dict
    """
    # At the beginning check whether incoming payload is a list, if so parse it per item.
    if isinstance(rows, list):
        if not target_object:
            target_object = []

        for row in rows:
            target_object.append(generic_payload_parser(row, metadata, {}))

    # If the payload contains more rows, loop over these rows and parse them per item.
    elif rows.get('f') and isinstance(rows['f'], list) and isinstance(metadata, list):
        if len(rows['f']) != len(metadata):
            logging.warn('Invalid matching!')
            return target_object
        for index, row in enumerate(rows['f']):
            output = generic_payload_parser(row, metadata[index], target_object)
            if metadata[index]['field'] not in target_object:
                target_object.update({metadata[index]['field']: output})

    # If the payload has list type and the metadata doesn't, it is a repeated object. Such as tag properties or datasource channels.
    elif rows.get('v') is not None and isinstance(rows['v'], list) and not isinstance(metadata, list) and metadata['field'] and metadata['items']:
        target_object[metadata['field']] = generic_payload_parser(rows['v'], metadata, [])

    # If the payload is an object containing a list, parse the object
    elif rows.get('v') and isinstance(rows['v'], dict) and rows['v'].get('f') and isinstance(rows['v']['f'], list) and isinstance(metadata, list):
        target_object.update(generic_payload_parser(rows['v'], metadata, target_object))

    # If the payload is a property parse the property to the correct format.
    elif rows.get('v') and metadata['field']:
        if metadata['type'] == 'string':
            target_object[metadata['field']] = rows['v']
        elif metadata['type'] == 'record':
            target_object = generic_payload_parser(rows['v'], metadata['items'], {})
        elif metadata['type'] == 'timestamp':
            if str(rows['v']).isdigit():
                target_object[metadata['field']] = rows['v'] * 10**9
            elif 'E' in rows['v']:
                target_object[metadata['field']] = float(rows['v']) * 10**9
            else:
                target_object[metadata['field']] = rows['v']
        elif metadata['type'] == 'datetime':
            target_object[metadata['field']] = rows['v']
        elif metadata['type'] == 'float':
            target_object[metadata['field']] = float(rows['v'])
        elif metadata['type'] == 'integer':
            target_object[metadata['field']] = int(rows['v'])
        elif metadata['type'] == 'boolean':
            target_object[metadata['field']] = bool(rows['v'])
        else:
            logging.warn('Unsupported type: %s containing value %s', metadata['type'], rows['v'])

    # If record type, loop over the items and parse them.
    elif rows.get('f') and metadata['type'] == 'record':
        target_object[metadata['field']] = []
        for row in rows.get('f'):
            target_object[metadata['field']].append(generic_payload_parser(row, metadata['items'], {}))
    else:
        logging.warn('Invalid scenario! %s', rows)
    return target_object