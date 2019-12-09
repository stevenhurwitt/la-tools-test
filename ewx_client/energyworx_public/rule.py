import inspect
from abc import ABCMeta, abstractmethod
from datetime import datetime

HEARTBEAT_COLUMN = '_HEARTBEAT'
HEARTBEAT_COLUMN_TEMPLATE = '{}%s' % HEARTBEAT_COLUMN
PREPARE_DATASOURCE_IDS_KEY = 'prepare_datasource_ids'


class BaseRule:
    __metaclass__ = ABCMeta

    def __init__(self, dataframe=None):
        """
        Abstract implementation of the pluggable rule
        Args:
            dataframe (DataFrame):
        """
        self.dataframe = dataframe

    @classmethod
    def get_rule_attributes(cls):
        return [x for x in inspect.getargspec(getattr(cls, 'apply')).args if x != 'self']

    @classmethod
    def get_function_name(cls):
        return cls.__module__.split('.')[-1]

    @abstractmethod
    def apply(self, **kwargs):
        pass


class AbstractTransformRule(BaseRule):
    __metaclass__ = ABCMeta

    def __init__(self, dataframe, result, adapted_data, mapping, datasources):
        super(AbstractTransformRule, self).__init__(dataframe)
        self.result = result
        self.adapted_data = adapted_data
        self.mapping = mapping
        self.datasources = datasources


class AbstractRule(BaseRule):
    __metaclass__ = ABCMeta

    def __init__(self, datasource, dataframe=None, detectors=None, source_column=None, destination_column=None, sequence_index=None, data_filter=None, billing_account_id=None, namespace=None,
                 flow_properties=None):
        """
        Abstract implementation of the pluggable rule
        Args:
            datasource (Datasource):
            dataframe (DataFrame):
            detectors (dict):
            source_column (str):
            destination_column (str):
            sequence_index (int):
            data_filter (Series):
            namespace (Namespace):
            flow_properties (dict[str, str]):
        """
        super(AbstractRule, self).__init__(dataframe)
        self.datasource = datasource
        self.detectors = detectors
        self.source_column = source_column
        self.source_heartbeat_column = HEARTBEAT_COLUMN_TEMPLATE.format(source_column)
        self.destination_column = destination_column
        self.destination_heartbeat_column = HEARTBEAT_COLUMN_TEMPLATE.format(destination_column)
        self.sequence_index = sequence_index
        self.rule_datasources = None
        # If no datafilter present, return True where dataframe[source_column] is not nan (could happen in Dataflow crunch).
        # Otherwise return boolean True (happens in crunch_queue)
        self.data_filter = data_filter if data_filter is not None else dataframe[source_column] == dataframe[source_column] if (dataframe is not None and source_column is not None) else True
        self.side_input = None
        self.calculate_model_result = None
        self.billing_account_id = billing_account_id
        self.namespace = namespace
        self.flow_properties = flow_properties if flow_properties is not None else {}
        self.context = {}
        self.annotation_whitelist = []
        self.annotation_blacklist = []

    def prepare_context(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:
            dict:

        """
        return {}

    def load_timeslice_group(self, timeslice_group_id):
        """

        Args:
            timeslice_group_id (str):

        Returns:
            TimesliceGroup:
        """
        raise NotImplementedError('This function is only accessible during prepare_context')

    def load_timeslice_groups_by_name(self, timeslice_group_name):
        """

        Args:
            timeslice_group_name (str):

        Returns:
            list(TimesliceGroup):
        """
        raise NotImplementedError('This function is only accessible during prepare_context')

    def load_datasource(self, datasource_id):
        """

        Args:
            datasource_id (str):

        Returns:
            Datasource:
        """
        raise NotImplementedError('This function is only accessible during prepare_context')

    def load_channel_classifier(self, channel_classifier_name):
        """

        Args:
            channel_classifier_name (str):

        Returns:
            ChannelClassifier:
        """
        raise NotImplementedError('This function is only accessible during prepare_context')

    def execute_eql(self, eql_query):
        """

        Args:
            eql_query (str):

        Returns:
            list[str]: A list of found datasource id's
        """
        raise NotImplementedError('This function is only accessible during prepare_context')

    def load_side_input(self, datasource_id, channel_id, start, end, sequence_destination_channel_id=None, load_annotations=False):
        """

        Args:
            datasource_id (str):
            channel_id (str):
            start (datetime):
            end (datetime):
            sequence_destination_channel_id (str): this is only used to load an sequence destination channel, where the channel_id (second arguement) should be flow destination channel id
            load_annotations (bool):

        Returns:
            pd.Dataframe:
        """
        raise NotImplementedError('This function is only accessible during apply')

    def additional_output(self, filename, file_content, tags):
        """

        Args:
            filename (str): Name of the file
            file_content (str): Content of the file
            tags (list[str]): Optional tags which should be set on the file
        """
        raise NotImplementedError('This function is only accessible during apply')


class RuleResult:

    def __init__(self, result=None, detectors=None, aggregates=None, flow_metadata_properties=None):
        """
        RuleResult that contains the information that the apply function of the AbstractRule returns
        Args:
            result (DataFrame): the resulting dataframe
            detectors (List[Detector]): the list of detectors
            aggregates (List[Aggregate]): the list of Aggregate
            flow_metadata_properties (dict): the additional flow_metadata_properties
        """
        self.result = result
        self.detectors = detectors
        self.aggregates = aggregates
        self.flow_metadata_properties = flow_metadata_properties


class Detector:
    def __init__(self, detector, function_name, start_timestamp, end_timestamp, value, properties=None):
        """
        Detector class containing detected feature
        Args:
            detector (str): The name of the detector
            function_name (str): the name of the function that holds the detector rule
            start_timestamp (datetime): The start timestamp of the detected feature
            end_timestamp (datetime): The end timestamp of the detected feature
            value (str): String value of the feature
            properties (List[dict]): Optional list of properties (key/values)
        """
        self.detector = detector
        self.function_name = function_name
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.value = value
        self.properties = properties
