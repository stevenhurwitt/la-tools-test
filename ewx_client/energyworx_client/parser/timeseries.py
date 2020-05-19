from __future__ import print_function

from energyworx_client.parser import generic_payload_parser


def parse_result_df(result):
    """

    Args:
        result (dict):

    Returns:
        pd.DataFrame
    """
    import pandas as pd
    df_values = {'timestamp': result.get('dataframe').get('index').get('values')}
    for values in result.get('dataframe').get('data'):
        update = {values.get('name'): values.get('values')}
        df_values.update(update)
    return pd.DataFrame.from_dict(df_values).set_index('timestamp')


def parse_nested_structure_result_df(result):
    """

    Args:
        result (dict):

    Returns:
        DataFrame
    """
    rows = result['rows']
    metadata = result['metadata']['fields']
    try:
        return to_dataframe(generic_payload_parser(rows, metadata))
    except KeyError:
        return result


def to_dataframe(output):
    """

    Args:
        output (list):

    Returns:
        pd.DataFrame
    """
    import pandas as pd
    data_type = 'flow'
    if output and 'datasource' in output[0].get('row'):
        data_type = 'datasource'  # Use the first row to decide if this datasets contains flow or raw data
    channels = set()
    for row in output:
        for channel in row['row'][data_type]['channel']:
            channels.update([channel['channel_classifier_id']])

    channel_datapoints = {}
    for channel in channels:
        channel_datapoints.update({channel: {}})

    for row in output:
        timestamp = row['row']['timestamp']
        channels = row['row'][data_type]['channel']
        for channel in channels:
            channel_datapoints[channel['channel_classifier_id']][timestamp] = channel['value']

    data = pd.DataFrame(data=channel_datapoints)
    data.index = pd.to_datetime(data.index)
    return data
