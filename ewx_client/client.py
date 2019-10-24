import logging
import os
import socket
import requests
import time
import re
import urllib
from retrying import retry

from googleapiclient.errors import HttpError

from auth import DEFAULT_API_ROOT
from auth.external_service import ExternalService
from parser.tags import parse_tags
from parser.timeseries import parse_result_df, parse_nested_structure_result_df

logger = logging.getLogger()


class EWX(object):

    def __init__(self, namespace_id=None, api_root=None, credentials=None):
        super(EWX, self).__init__()
        if not namespace_id:
            namespace_id = os.environ.get('EWX_NAMESPACE')
            logger.warning("No namespace parameter could be found, so we are using the primary namespace of the user")
        if not api_root:
            api_root = DEFAULT_API_ROOT
        self.namespace_id = namespace_id
        self.api_root = api_root
        logger.info('Using namespace = %s and api_root = %s', namespace_id, api_root)
        self.client = ExternalService.get_client(api_root=api_root, credentials=credentials)

    # ChannelClassifier
    def get_channel_classifier(self, name):
        """Get a channel classifier by name

        Args:
            name (str): The name of the channel classifier

        Returns:
            dict: A dictionary describing the channel classifier

        """
        request = self.client.channelclassifier().classifier().get(name=name)
        return self.__execute_and_handle_response(request)

    def create_channel_classifier(self, id, name, unit_type, datapoint_type, description=None):
        """Create a channel classifier by name

        Args:
            id (str):
            name (str): The name of the channel classifier
            unit_type (str):
            datapoint_type (str):
            description (str):

        Returns:
            dict: A dictionary describing the channel calssifier

        """
        body = {'id': name,
                'unitType': unit_type,
                'name': name,
                'description': description,
                'datapointType': datapoint_type}
        request = self.client.channelclassifier().classifier().create(body=body)
        return self.__execute_and_handle_response(request)

    # RunConfig
    def create_flowconfig(self, name, description=None, enabled=None, flow_type="scenario", sequence_configs=None, destination_channel_classifier=None):
        """ Creates a new flow configuration.

        A flow configuration can consist of several sequence configurations that are
        executed one after the other. An example sequence_configs argument is:
        sequence_configs = [
          {
            "name": "sequence1",
            "description": "sequence 1",
            "sourceColumn": "RAW",
            "destinationColumn": "VEE_RESULT",
            "ruleConfigs": [
              {
                "function": "gap_check",
                "type": "validation",
                "displayName": "Gap Check"
              },
              {
                "function": "zero_reads",
                "type": "validation",
                "displayName": "Zero Reads"
              },
            ]
          },
          {
            "name": "sequence2",
            "description": "sequence 2",
            "sourceColumn": "VEE_RESULT",
            "destinationColumn": "VEE_RESULT",
            "ruleConfigs": [
              {
                "function": "like_day_substitution",
                "type": "validation",
                "displayName": "Like Day Substitution",
                "filterWhitelist": [gap_check:0, zero_reads:0]
              }
            ]
          }
        ]

        Args:
            name (str): Name of the flow configuration.
            description (str): Description of the flow configuration.
            enabled (bool): A boolean indicating whether the configuration can be used.
            flow_type (str): "scenario" or "continuous"
            sequence_configs (list[dict]): A list of sequence configuration dictionaries.
                Each sequence configuration can have a name, description,
                destination column and a ruleConfigs key that takes a list.
            destination_channel_classifier (str): classifier that will be used to store
                flow metadata with. It's optional; if it is not provided, the destinationColumn
                of the latest sequence will be used as the destination_channel_classifier.

        Returns:
            dict: A dictionary with the created flow configuration and its ID.
        """
        body = {'name': name,
                'description': description,
                'enabled': enabled,
                'flowType': flow_type,
                'sequenceConfigs': sequence_configs,
                'destinationChannelClassifier': destination_channel_classifier}
        request = self.client.runconfig().runconfig().create(body=body)
        return self.__execute_and_handle_response(request)

    def get_upload_url(self, market_adapter_id=None, tags=None, use_streaming=False):
        request = self.client.storage().storage().files().uploadurl(marketAdapterId=market_adapter_id, tags=tags, useStreaming=use_streaming)
        return self.__execute_and_handle_response(request)

    def get_flowconfig(self, id):
        """ Gets a flow configuration by identifier.

        Args:
            id (str): The ID of the flow configuration.

        Returns:
            dict: A dictionary describing the flow configuration.
        """
        request = self.client.runconfig().runconfig().get(id=id)
        return self.__execute_and_handle_response(request)

    def update_flowconfig(self, id, name, description=None, enabled=None, flow_type='scenario', sequence_configs=None, destination_channel_classifier=None):
        """Updates a flow configuration with the given ID using the parameters given.

        One or more arguments can be updated at once, unused arguments are not affected.

        Args:
            id (str) The ID of the flow configuration.
            name (str): Name of the flow configuration.
            description (str): Description of the flow configuration.
            enabled (bool): A boolean indicating whether the configuration can be used.
            flow_type (str): "scenario" or "continuous"
            sequence_configs (list[dict]): A list of sequence configuration dictionaries.
                Each sequence configuration can have a name, description,
                destination column and a ruleConfigs key that takes a list.
            destination_channel_classifier (str): classifier that will be used to store
                flow metadata with. It's optional; if it is not provided, the destinationColumn
                of the latest sequence will be used as the destination_channel_classifier.

        Returns:
            dict: A dictionary describing the updated flow configuration.
        """
        body = {'id': id,
                'name': name,
                'description': description,
                'enabled': enabled,
                'flowType': flow_type,
                'sequenceConfigs': sequence_configs,
                'destinationChannelClassifier': destination_channel_classifier}
        request = self.client.runconfig().runconfig().update(body=body)
        return self.__execute_and_handle_response(request)

    def list_flowconfigs(self, enabled=True, deleted=False, limit=20, page_token=None):
        """ Gets a list of flow configurations that match the given filters.

        Args:
            enabled (bool): A boolean describing whether the flow configuration can be used.
            deleted (bool): A boolean describing whether the flow configuration is deleted.
            limit (int): How many results to return as an int.
            page_token (None or str): A page_token identifier to retrieve more results.

        Returns:
            dict: A dictionary with flow configurations, possibly a pageToken and an
                identifier whether there are more results.
        """
        request = self.client.runconfig().runconfig().list(enabled=enabled, deleted=deleted, limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    def delete_flowconfig(self, id):
        """ Deletes a flow configuration with the given ID.

        Args:
            id (str): The ID of the flow configuration.

        Returns:
            dict: A dictionary with the flow configuration including a key deleted.
        """
        request = self.client.runconfig().runconfig().delete(id=id)
        return self.__execute_and_handle_response(request)

    # Rules
    def create_rules(self, items):
        """ Creates rules based on the specification(s) in items.

        Args:
            items (list[dict]): A list of rule specifications.

        Returns:
            dict: A dictionary with number of successfully created rules.
        """
        body = {'items': items}
        request = self.client.rule().rule().create(body=body)
        return self.__execute_and_handle_response(request)

    def get_rule(self, name):
        """ Gets a rule description based on its name.

        Args:
            name (str): Name of the rule.

        Returns:
            dict: A dictionary with the rule parameters.
        """
        request = self.client.rule().rule().get(name=name)
        return self.__execute_and_handle_response(request)

    def list_rules(self, rule_type):
        """ Lists all rules of specified type.

        Args:
            rule_type (str): Which type of rules to list.

        Returns:
            dict: A dictionary which contains a list of rule dictionaries, possibly a page token
            and an indicator whether there are more results.
        """
        request = self.client.rule().rule().list(ruleType=rule_type)
        return self.__execute_and_handle_response(request)

    def update_rule(self, name, rule_type, display_name=None, description=None, params=None, code_blob=None):
        """ Updates an existing rule defined by its name and type.

        Args:
            name (str): Name of the rule.
            rule_type (str): Type of the rule.
            display_name (str): Display name of the rule.
            description (str): Description of the rule.
            params (list): Rule parameters.
            code_blob (str): Code blob describing the rule (not yet available).

        Returns:
            dict: A dictionary with the updated rule parameters.
        """
        body = {'name': name,
                'displayName': display_name,
                'description': description,
                'ruleType': rule_type,
                'params': params,
                'codeBlob': code_blob}
        request = self.client.rule().rule().update(body=body)
        return self.__execute_and_handle_response(request)

    def remove_rule(self, name):
        """ Removes a rule.

        Args:
            name (str): Name of the rule.

        Returns:
            dict: An empty dictionary.
        """
        request = self.client.rule().rule().delete(name=name)
        return self.__execute_and_handle_response(request)

    def list_ruletypes(self, limit=20, page_token=None):
        """ Lists rule types.

        Args:
            limit (int): How many rule types to return.
            page_token (None or str): A token to fetch further results.

        Returns:
            dict: A dictionary of rule types.
        """
        request = self.client.rule().rule().ruletype().list(limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    def prototype_rule(self, name):
        """ Prepares a rule for prototyping.

        Args:
            name (str): Name of the rule.

        Returns:
            dict: A dictionary with the name of the rule
        """
        request = self.client.rule().rule().prototype(name=name, body={})
        return self.__execute_and_handle_response(request)

    def release_rule(self, name):
        """ Releases a prototyped rule.

        Args:
            name (str): Name of the rule.

        Returns:
            dict: A dictionary with the name of the rule
        """
        request = self.client.rule().rule().release(name=name, body={})
        return self.__execute_and_handle_response(request)

    # Datasource
    def create_datasources(self, body):
        """ Creates new datasources with the given properties.

        Args:
            body(dict): the datasources request body

        Returns:
            dict: A dictionary with the ID and creation time of the new datasources.
        """
        request = self.client.flow().datasources().create(body=body)
        return self.__execute_and_handle_response(request)

    def create_datasource(self, body):
        """ Creates a new datasource with the given properties.

        Args:
            body(dict): the datasource request body

        Returns:
            dict: A dictionary with the ID and creation time of the new datasource.
        """
        request = self.client.datasource().datasource().create(body=body)
        return self.__execute_and_handle_response(request)

    def get_datasource(self, id):
        """ Gets a datasource by identifier.

        Args:
            id (str): A datasource identifier as a string.

        Returns:
            dict: A datasource dictionary.
        """
        request = self.client.datasource().datasource().get(id=id)
        return self.__execute_and_handle_response(request)

    def list_datasources(self, limit=20, page_token=None):
        """ Lists datasources.

        Args:
            limit (int): How many datasources to return at most as an integer.
            page_token (str or None):

        Returns:
            dict: A dictionary with a list of datasource dictionaries, possibly
                a page token and an indicator whether there are more results.
        """
        request = self.client.datasource().datasources().list(limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    def list_channel_classifiers(self, limit=None, order=None, page_token=None):
        """ Lists channel classifiers.

        Args:
            limit (int): How many channel classifiers to return.
            order (str): A key of channel classifier dictionary to use for sorting.
            page_token (str or None): A token to fetch further results.

        Returns:
            dict: A dictionary with a list of channel classifier dictionaries and
                possibly a page token.
        """
        request = self.client.datasource().channels().classifier().list(limit=limit, order=order, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    def update_channel_classifier(self, name, new_name, description):
        """ Updates a channel classifier.

        Args:
            name (str): Name of the channel classifier.
            new_name (str): New name of the channel classifier.
            description (str): New description of the channel classifier.

        Returns:
            dict: A dictionary with the updated channel classifier.
        """
        body = {'name': name,
                'newName': new_name,
                'description': description}
        request = self.client.datasource().channels().classifier().update(body=body)
        return self.__execute_and_handle_response(request)

    def add_channels(self, id, channels):
        """ Adds channels to a datasource.

        Args:
            id (str): The ID of the datasource.
            channels (list[dict]): A list of channels.

        Returns:
            dict: A dictionary with the ID of the datasource and update time.
        """
        body = {'id': id,
                'channels': channels}
        request = self.client.datasource().channels().add(body=body)
        return self.__execute_and_handle_response(request)

    def remove_channels(self, id, channels):
        """ Removes channels from a datasource.

        Args:
            id (str): The ID of the datasource.
            channels (list): A list of channels to be removed. Each dictionary
                needs to contain at least the id and classifier of the channel.

        Returns:
            dict: A dictionary with the ID of the datasource and update time.
        """
        body = {'id': id,
                'channels': channels}
        request = self.client.datasource().channels().remove(body=body)
        return self.__execute_and_handle_response(request)

    # Query
    def execute_query(self, query, job_id=None, limit=10, page_token=None, raw_result=False, priority='interactive'):
        """ Execute an EQL query.

        Args:
            query (str): The query as a string.
            job_id (str): if provided, it will try to fetch the result from this job id
            limit (int):
            page_token (str or None):
            raw_result (bool): return raw JSON result from API or parse into dataframe

        Returns:
            str or dict or pd.DataFrame: Results of the query in a dataframe.
        """
        job_complete = False
        while not job_complete:
            request = self.client.query().query().execute(query=query, jobId=job_id, limit=limit, pageToken=page_token, priority=priority)
            result = self.__execute_and_handle_response(request)
            job_complete = result['reference'].get('jobComplete', True)
            job_id = result['reference'].get('jobId')
            time.sleep(0.1)
        if isinstance(result, str) or raw_result:
            return result
        try:
            return parse_result_df(result=result)
        except Exception:
            pass
        try:
            return parse_nested_structure_result_df(result=result)
        except Exception:
            pass
        try:
            return parse_tags(result=result)
        except Exception:
            pass

    def search_files(self, filename=None, tags=None, read_only=None, created_date=None, user_id=None, market_adapter_id=None, limit=None, page_token=None):
        request = self.client.storage().storage().files().search(filename=filename, tags=tags,
                                                                 readOnly=read_only, createdDate=created_date,
                                                                 userId=user_id, marketAdapterId=market_adapter_id,
                                                                 limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    def ingest_files(self, market_adapter_id=None, use_streaming=False, file_locations=None):
        request = self.client.storage().storage().files().ingest(body=dict(marketAdapterId=market_adapter_id, useStreaming=use_streaming,
                                                                 fileLocations=file_locations))
        return self.__execute_and_handle_response(request)


    # Tag
    def list_tags(self, limit=None, page_token=None):
        """ Lists used tags.

        Args:
            limit (int): How many results to return.
            page_token (str or None): Retrieve more results starting from previous results.

        Returns:
            dict: A dictionary with a list of used tags, possibly a page token and an
                indicator whether there are more results.
        """
        request = self.client.tag().tag().name().list(limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    # TODO: Fix the API call (EWXP-1517)
    # def get_tag_versions(self, datasource_ids, tag_filter, limit, page_token):
    #     """
    #
    #     Args:
    #         datasource_ids:
    #         tag_filter:
    #         limit:
    #         page_token:
    #
    #     Returns:
    #
    #     """
    #     request = self.client.tag().tag().versions().get(
    #         datasourceIds=datasource_ids, tagFilter=tag_filter, limit=limit, pageToken=page_token)
    #     return self.__execute_and_handle_response(request)

    def add_tags(self, tags):
        """ Adds tags to a datasource.

        Args:
            tags: A list of tag dictionaries.

        Returns:
            dict: A dictionary with the number of added tags and a creation time.
        """
        request = self.client.tag().tag().add(body=tags)
        return self.__execute_and_handle_response(request, async=True)

    def update_tags(self, tags):
        """ Updates tags of a datasource.

        Args:
            tags: A list of tag dictionaries.

        Returns:
            dict: A dictionary with the number of updates tags and an update time.
        """
        request = self.client.tag().tag().update(body=tags)
        return self.__execute_and_handle_response(request, async=True)

    def remove_tags(self, tags):
        """ Removes tags of a datasource.

        Args:
            tags: A list of tag dictionaries.

        Returns:
            dict: A dictionary with the number of removed tags and a removal time.
        """
        request = self.client.tag().tag().remove(body=tags)
        return self.__execute_and_handle_response(request, async=True)

    def get_flow_metadata(self, flow_id):
        """ Get flow metadata based on the flow id.

        Args:
            flow_id: The flow identifier as a string.

        Returns:
            dict: A dictionary of flow metadata.
        """
        raise NotImplementedError('This functionality is not supported')

    def list_flow_classifiers(self, datasource_id):
        """ List flow classifiers based on a datasource id.

        Args:
            datasource_id: The datasource id as a string.

        Returns:
            dict: A dictionary with flow classifiers in key items as a list and an indicator whether there are more results
            in key more. If there are more results, also a pageToken is returned in the dictionary.
        """
        # TODO: limit and pageToken arguments not working
        request = self.client.run().run().classifier().datasource().list(datasourceId=datasource_id)
        return self.__execute_and_handle_response(request)

    def list_flows(self, datasource_ids=None, flow_id=None, flow_date=None, flow_type=None, channel_classifiers=None, completed=None, approved=None, page_token=None):
        """ List flows for a datasource id.

        Args:
            datasource_ids list[str]: The datasource ids
            flow_id (str): Search for an exact flow ID
            flow_date (str): only search on a specific date
            flow_type (str): "scenario" or "continuous"
            channel_classifiers list[str]: Optional channel classifier id as a string to return only that channel classifier.
            completed (bool): indicates to filter for only completed flows (if True)
            approved (bool): indicates to filter for only approved flows (if True)
            page_token (str or None): used when results are paged

        Returns:
            dict: A dictionary with flows in items key and indicator whether there are more results in key more.
                If there are more results, also a pageToken is returned in the dictionary.
        """
        job_id = None
        job_complete = False
        while not job_complete:
            request = self.client.run().run().search(datasourceIds=datasource_ids, flowId=flow_id, flowDate=flow_date, flowType=flow_type, channelClassifiers=channel_classifiers, completed=completed, approved=approved, pageToken=page_token, jobId=job_id)
            result = self.__execute_and_handle_response(request)
            job_id = result['jobId']
            job_complete = 'items' in result and result['jobId']
            time.sleep(0.1)
        return result

    def start_flow(self, datasource_identifiers, source_classifier, flowconfiguration_id, start_datetime, end_datetime, use_streaming=False, persist=True):
        """ Starts a new flow. Example request body that is being built up:

        {
            "startDatetime": "string",
            "endDatetime": "string",
            "useStreaming": true,
            "datasourceIds": [
                "string"
            ],
            "persist": true,
            "sourceClassifier": "string",
            "flowConfigurationId": "string"
        }

        Args:
            datasource_identifiers (list[str]): datasource identifiers to start flows for
            source_classifier (str): classifier to start the flow for
            flowconfiguration_id (str): id of the flow configuration to use
            start_datetime (str): start date of timeseries data to use. Format of datetime
                %Y-%m-%dT%H:%M:%S.%f (example 2017-03-18T00:00:00.000). The time is assumed
                to be in UTC.
            end_datetime (str): end date of the timeseries data to use. Format of datetime
                %Y-%m-%dT%H:%M:%S.%f (example 2018-02-24T00:00:00.000). The time is assumed
                to be in UTC.
            use_streaming (bool): whether to start the flow in streaming mode or in batch mode.
                It is advised to start a lot of flows (a big batch) in batch mode. If you'd only
                like to start one or a few flows, streaming is the way to go.
            persist (bool): indicates whether to store the flow result. If not, then the result
                can be polled later on. NOTE; THIS IS NOT SUPPORTED YET. BY DEFAULT IT WILL BE
                SET TO TRUE FOR NOW.

        Returns:
            dict: A dictionary with referenceId and a list named datasourcesRunStarted.
        """
        body = {"startDatetime": start_datetime,
                "endDatetime": end_datetime,
                "useStreaming": use_streaming,
                "datasourceIds": datasource_identifiers,
                "persist": True,
                "sourceClassifier": source_classifier,
                "flowConfigurationId": flowconfiguration_id}
        request = self.client.run().run().start(body=body)
        return self.__execute_and_handle_response(request)

    # =================
    # Transport Adapter
    # =================

    def create_transport_adapter(self, name, description, type, market_adapter_id, properties):
        """ Create a transport adapter configuration

        Args:
            name (str):
            description (str):
            type (str):
            market_adapter_id (str):
            properties (dict[str, str]):

        Returns:
            object:
        """
        prepared_properties = [dict(key=kv, value=properties[kv]) for kv in properties] if properties else {}
        body = dict(name=name, description=description, type=type, market_adapter_id=market_adapter_id, properties=prepared_properties)
        request = self.client.transportadapters().transportadapters().create(body=body)
        return self.__execute_and_handle_response(request)

    def list_transport_adapters(self, limit=None, page_token=None):
        """ Retrieves a list of transport adapter configurations

        Args:
            limit (str):
            page_token (str):

        Returns:
            object:
        """
        request = self.client.transportadapters().transportadapters().list(limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)

    def get_transport_adapter(self, transport_adapter_id):
        """ Retrieves a single transport adapter configuration

        Args:
            transport_adapter_id (str):

        Returns:
            object:
        """
        request = self.client.transportadapters().transportadapters().get(id=transport_adapter_id)
        return self.__execute_and_handle_response(request)

    def update_transport_adapter(self, transport_adapter_id, name, description, type, market_adapter_id, properties):
        """ Updates a transport adapter configuration

        Args:
            transport_adapter_id (str):
            name (str):
            description (str):
            type (str):
            market_adapter_id (str):
            properties (list[dict[str, str]):

        Returns:
            object:
        """
        prepared_properties = [dict(key=kv, value=properties[kv]) for kv in properties] if properties else {}
        body = dict(name=name, description=description, type=type, market_adapter_id=market_adapter_id, properties=prepared_properties)
        request = self.client.transportadapters().transportadapters().update(id=transport_adapter_id, body=body)
        return self.__execute_and_handle_response(request)

    def patch_transport_adapter(self, transport_adapter_id, description=None, type=None, market_adapter_id=None, properties=None, adapter_data=None):
        """ Patches a transport adapter configuration

        Args:
            transport_adapter_id (str):
            description (str):
            type (str):
            market_adapter_id (str):
            properties (list[dict[str, str]):
            adapter_data (str):

        Returns:
            object:
        """
        body = dict()
        if description is not None:
            body['description'] = description
        if type is not None:
            body['type'] = type
        if market_adapter_id is not None:
            body['marketAdapterId'] = market_adapter_id
        if properties is not None:
            body['properties'] = [dict(key=kv, value=properties[kv]) for kv in properties] if properties else {}
        if adapter_data is not None:
            body['adapterData'] = adapter_data
        request = self.client.transportadapters().transportadapters().patch(id=transport_adapter_id, body=body)
        return self.__execute_and_handle_response(request)

    def add_transport_adapter_property(self, transport_adapter_id, properties):
        """ Adds properties to a transport adapter configuration

        Args:
            transport_adapter_id (str):
            properties (dict[str, str]:

        Returns:
            object:
        """
        body = dict(properties=[dict(key=_key, value=properties[_key]) for _key in properties] if properties else {})
        request = self.client.transportadapters().transportadapters().properties().add(id=transport_adapter_id, body=body)
        return self.__execute_and_handle_response(request)

    def add_channel_classifier(self, unit_type, description, name, datapoint_type):
        """ Adds a channel classifier

        Args:
            unit_type (str):
            description (bool):
            name (str):
            datapoint_type (str):

        Returns:
            object:
        """
        body = dict(unitType=unit_type, description=description, name=name, datapointType=datapoint_type)
        request = self.client.channelclassifier().classifier().create(body=body)
        return self.__execute_and_handle_response(request)

    def get_transport_adapter_property(self, transport_adapter_id, key):
        """ Retrieves a single property from a transport adapter configuration

        Args:
            transport_adapter_id (str):
            key (str):

        Returns:
            object:
        """
        request = self.client.transportadapters().transportadapters().properties().get(id=transport_adapter_id, key=key)
        return self.__execute_and_handle_response(request)

    def delete_transport_adapter(self, transport_adapter_id):
        """ Deletes a transport adapter configuration

        Args:
            transport_adapter_id (str):

        Returns:
            object:
        """
        request = self.client.transportadapters().transportadapters().delete(id=transport_adapter_id)
        return self.__execute_and_handle_response(request)

    def trigger_transport_adapter(self, transport_adapter_id):
        """ Triggers a transport adapter

        Args:
            transport_adapter_id (str):

        Returns:
            object:
        """
        request = self.client.transportadapters().transportadapters().trigger(id=transport_adapter_id, body={})
        return self.__execute_and_handle_response(request)

    def create_iot_register(self, name, description, number_of_streaming_buffers, streaming_buffer_window, market_adapter_id, buffer_processing_market_adapter_id):
        """

        Args:
            name (str):
            description (str):
            number_of_streaming_buffers (int):
            streaming_buffer_window (int):
            market_adapter_id (str):
            buffer_processing_market_adapter_id (str):

        Returns:
            object:
        """
        body = {
            "name": name,
            "description": description,
            "numberOfStreamingBuffers": number_of_streaming_buffers,
            "streamingBufferWindow": streaming_buffer_window,
            "marketAdapterId": market_adapter_id,
            "bufferProcessingMarketAdapterId": buffer_processing_market_adapter_id
        }
        request = self.client.iot().iot().registers().create(body=body)
        return self.__execute_and_handle_response(request)

    def create_iot_device(self, iot_register_name, device_id, blocked):
        """ Will create an IOT device for the provided IOT register

        Args:
            iot_register_name (str):
            device_id (str):
            blocked (bool):

        Returns:
            object:
        """
        body = {
            "id": device_id,
            "blocked": blocked
        }
        request = self.client.iot().iot().devices().create(iotRegisterName=iot_register_name, body=body)
        return self.__execute_and_handle_response(request)

    def get_timeslice_group(self, timeslice_group_id):
        """ Retrieves a timeslice group object

        Args:
            timeslice_group_id (str):

        Returns:
            dict:
        """
        request = self.client.timeslice().timeslice().get(id=timeslice_group_id)
        return self.__execute_and_handle_response(request)

    def read_iot_buffer(self, register_name, device_id, number_of_buffers=None, column_filter=None, start_datetime=None):
        """ Reads (an) iot buffer(s)

        Args:
            register_name (str):
            device_id (str):
            number_of_buffers (int):
            column_filter (list[str]):
            start_datetime (int):

        Returns:
            object:
        """
        request = self.client.iot().iot().buffer().read(registerName=register_name,
                                                        deviceId=device_id)
        query_params = {}
        if number_of_buffers is not None:
            query_params['numberOfBuffers'] = number_of_buffers
        if column_filter is not None:
            query_params['columnFilter'] = column_filter
        if start_datetime is not None:
            query_params['startDatetime'] = start_datetime
        if query_params:
            request.uri += '&{}'.format(urllib.urlencode(query_params))
        result = self.__execute_and_handle_response(request)
        return parse_nested_structure_result_df(result=result)

    def __update_namespace(self, request, async=False):
        request.headers.update({'x-namespace': self.namespace_id})
        if async:
            request.headers.update({'x-async-request': async})
        return request

    def __execute_and_handle_response(self, request, async=False):
        try:
            updated_request = self.__update_namespace(request, async)
        except Exception as ex:
            logger.error('Namespace could not be updated: %s', ex, exc_info=True)
            raise Exception('Namespace could not be updated: {}'.format(ex))
        for count in range(2):
            try:
                return updated_request.execute(num_retries=3)
            except socket.error as socket_error:
                if socket_error.strerror == 'Connection reset by peer':
                    logger.info('%s -> retry', socket_error.strerror)
                    continue
            except HttpError:
                raise
            except Exception as ex:
                logger.error('Request failed: %s', ex, exc_info=True)
                raise Exception('Request failed: {}'.format(ex))

    def upload_file(self, filename, file_content=None, tags=None, adapter_id=None, streaming=False):
        """It is important to use the exact same way of uploading data when developing, so this function
        uploads files using the EDC way. First we get the upload url to blobstore via the API (using the
        EWX client) and then we upload to blobstore API. The prepare process is then triggered by GAE
        when a market adapter id is given.

        Args:
            filename (str): The filename to use when uploading
            file_content (str): The file contents to upload
            tags (list[str]): Tags that needs to be assigned to the file to be uploaded so it can be found in the filemanager
            adapter_id (str): The adapter id, if given, after the upload an ingest will be triggered with this market adapter id
            streaming (bool): When set to true, it will use the streaming pipeline

        Returns:
            object
        """
        def _retry_if_exception(exception):
            """ Specify an exception you need. or just True"""
            return isinstance(exception, RuntimeError)
            
        STOP_MAX_DELAY = 600000
        WAIT_EXPONENTIAL_MAX = 10000
        WAIT_EXPONENTIAL_MULTIPLIER = 1000
        @retry(retry_on_exception=_retry_if_exception, wait_exponential_multiplier=WAIT_EXPONENTIAL_MULTIPLIER, wait_exponential_max=WAIT_EXPONENTIAL_MAX, stop_max_delay=STOP_MAX_DELAY)
        def _do_upload(upload_url, files, data):
            logging.info("Using upload_url: %s", upload_url)
            response = requests.post(upload_url, files={filename: file_content},
                                     data=dict(adapter_id=adapter_id, streaming=streaming),
                                     headers={'X-NAMESPACE': self.namespace_id, 'Accept': 'application/json,application/vnd.ewx.v2'})
            if 200 <= response.status_code < 300:
                logging.info('File %s successfully uploaded', filename)
                return response
            else:    
                logging.error('File %s could not be uploaded. Error: %s %s', filename, response.status_code, response.reason)
                raise RuntimeError('File {} could not be uploaded. Error: {} {}'.format(filename, response.status_code, response.reason))
                
        if not file_content:
            raise RuntimeError("File content is required!")
        if tags is None:
            tags = []
        logger.info("Uploading %s to blobstore with size %s", filename, len(file_content))
        res = self.get_upload_url(tags=tags, market_adapter_id=adapter_id, use_streaming=streaming)
        if not res:
            raise RuntimeError("Did not get a valid response for upload url")
        upload_url = res.get('uploadUrl')
        if not upload_url:
            raise RuntimeError("Could not create an uploadUrl with filename %s, and adapter_id %s", filename, adapter_id)
        return _do_upload(upload_url, files={filename: file_content}, data=dict(adapter_id=adapter_id, streaming=streaming))

    def download_file(self, blob_key):
        request_url = self.api_root + '/files/get/' + blob_key
        credentials = ExternalService._get_credentials(None)
        import httplib2
        http = httplib2.Http(disable_ssl_certificate_validation=True, timeout=60)
        credentials.authorize(http)
        response, content = http.request(request_url, method='GET', headers={
            'X-NAMESPACE': self.namespace_id,
            'Accept': 'application/json,application/vnd.ewx.v2',
        })

        if 200 <= response.status < 300:
            return content
        else:
            raise RuntimeError('File download error: {} {}'.format(response.status, response.reason))


class EWXPool(object):

    _EWXPool__instance = None

    # Singleton pattern
    def __new__(cls, *args, **kwargs):
        if not EWXPool._EWXPool__instance:
            EWXPool._EWXPool__instance = object.__new__(cls)
        return EWXPool._EWXPool__instance

    def get_client(self, api_root=None, namespace_id=None, credentials=None):
        """
        Args:
            api_root (str or None):
            namespace_id (str or None): the namespace
            credentials (ServiceAccountCredentials or None): the credentials

        Returns:
            EWX: an EWX client
        """
        if not namespace_id:
            raise ValueError('namespace must be specified')

        client_name = '__ewx_client_' + namespace_id
        client = getattr(self, client_name, None)
        # Check if there is already a client for this region/namespace and check if the credentials are still valid
        if not client: # or client.credentials.expired:
            client = EWX(api_root=api_root, namespace_id=namespace_id, credentials=credentials)
            setattr(self, client_name, client)
        return client
