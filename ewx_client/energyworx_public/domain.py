import logging
import operator
from datetime import datetime

import pytz
import dateutil
from typing import List, Any, Union, Tuple

from energyworx_public.base import EnergyworxDomain, StructuredProperty, Property, EnumProperty, DateTimeProperty, MappingStructuredProperty, MappingProperty, MappingEnumProperty
from energyworx_public.enums import MappedFieldType, TransformationMapFunctionType, TagType, UnitType, VirtualDatasourceAggregationType, DatasourceType, DatapointType, TimeslicePeriodType

logger = logging.getLogger()
DATETIME_STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class FlowException(Exception):
    def __init__(self, *args, **kwargs):
        super(FlowException, self).__init__(*args, **kwargs)
        self.sequence_id = None
        self.rule_function = None
        self.traceback = None

    def set_traceback(self, traceback_string, remove_internal_functions=False):
        if remove_internal_functions:
            logger.info('Traceback before: %s', traceback_string)
            splits = traceback_string.split('\n')
            ids_to_remove = []
            for index, split in enumerate(splits):
                if ' File "' in split and '/' in split:
                    ids_to_remove.append(index)
                    if len(splits) > index + 1 and 'File "' not in splits[index + 1] and '/' not in splits[index + 1]:
                        ids_to_remove.append(index + 1)
            ids_to_remove.reverse()
            for index_id in ids_to_remove:
                if len(splits) > index_id:
                    removed_value = splits.pop(index_id)
                    logger.info('Traceback removed: %s', removed_value)
            traceback_string = '\n'.join(splits)
            logger.info('Traceback result: %s', traceback_string)
        if len(traceback_string) > 0:
            self.traceback = traceback_string


class FlowCancelException(Exception):
    pass


class SequenceCancelException(Exception):
    pass


class FlowRuleException(Exception):
    pass


class KeyValue(EnergyworxDomain):
    key = Property(name="key", required=True)
    value = Property(name="value", required=True)
    deleted = Property(name="deleted", default=False)

    def to_dict(self):
        return dict(key=self.key,
                    value=self.value,
                    read_only=self.read_only)
    @classmethod
    def from_dict(cls, keyvalue_dict):
        return KeyValue(key=keyvalue_dict.get('key'),
                        value=keyvalue_dict.get('value'),
                        read_only=keyvalue_dict.get('read_only'))


class KeyValueType(KeyValue):
    value_type = Property(name="type", required=True, default="String")


class Tag(EnergyworxDomain):
    tag = Property(name="tag", required=True)
    description = Property(name="description", default='No description')
    valid_from = DateTimeProperty(name="validFrom")
    properties = StructuredProperty(KeyValueType, name="properties", repeated=True)
    removed = Property(name="removed", default=False)
    version = DateTimeProperty(name="version")
    is_active_scd = Property(name="isActiveSCD", required=False)
    tag_links = Property(name="tagLinks", default=False)
    created_by = Property(name="createdBy", default=None)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        if not self.valid_from:
            self.valid_from = datetime(1900,1,1,0,0,0)
        if not self.version:
            self.version = datetime.utcnow()

    def get_property(self, property_key):
        return next((key_value.value for key_value in self.properties if key_value.key == property_key), None)

    def __eq__(self, other):
        if isinstance(other, Tag):
            if self.tag != other.tag:
                return False
            if ((self.valid_from is None and other.valid_from is not None) or
                    (self.valid_from is not None and other.valid_from is None)):
                return False
            if (self.valid_from is not None and other.valid_from is not None and
                    self.valid_from.replace(tzinfo=None) != other.valid_from.replace(tzinfo=None)):
                return False
            if self.description != other.description:
                return False
            if self.removed != other.removed:
                return False
            self_property_dict = {kv.key: kv.value for kv in self.properties}
            other_property_dict = {kv.key: kv.value for kv in other.properties}
            # check whether the two dictionaries are equal
            if self_property_dict != other_property_dict:
                return False
            return True
        else:
            return False

    def to_dict(self):
        return dict(tag=self.tag,
                    tag_links=self.tag_links,
                    description=self.description,
                    validFrom=self.valid_from.strftime(DATETIME_STRING_FORMAT) if self.valid_from else None,
                    properties=[property.to_dict() for property in self.properties],
                    version=self.version.strftime(DATETIME_STRING_FORMAT) if self.version else None,
                    removed=self.removed,
                    read_only=self.read_only,
                    created_by=self.created_by)

    @classmethod
    def from_dict(cls, tag_dict):
        return Tag(tag=tag_dict.get('tag'),
                   tag_links=tag_dict.get('tag_links', []),
                   description=tag_dict.get('description'),
                   valid_from=dateutil.parser.parse(tag_dict.get('validFrom')),
                   properties=[KeyValue.from_dict(keyvalue_dict) for keyvalue_dict in tag_dict.get('properties')] if tag_dict.get('properties') else None,
                   version=dateutil.parser.parse(tag_dict.get('version')),
                   removed=tag_dict.get('removed'),
                   read_only=tag_dict.get('read_only'),
                   created_by=tag_dict.get('created_by'))


class ChannelClassifier(EnergyworxDomain):
    unit_type = EnumProperty(UnitType, name="unitType", required=True)
    datapoint_type = EnumProperty(DatapointType, name="datapointType", required=True)
    default_flow_configuration_id = Property(name="defaultFlowConfigurationId", required=False)
    aggregation_type = EnumProperty(VirtualDatasourceAggregationType, required=False)
    timeslice_group_model_ids = Property(name='timesliceGroupIds', repeated=True)
    default_timeslice_group_model = Property(name='defaultTimesliceId')


class Channel(EnergyworxDomain):
    id = Property(name="id", required=True)
    deleted = Property(name="deleted")
    name = Property(name="name")
    classifier = Property(name="classifier", required=True)
    description = Property(name="description", default="No description")
    unit_type = EnumProperty(UnitType, name="unitType")
    datapoint_type = EnumProperty(DatapointType, name="datapointType")
    is_source = Property(name="isSource")
    flow_configuration_id = Property(name="flowConfigurationId", required=False)
    # the next property is only used by the VirtualDatasources
    aggregation_type = EnumProperty(VirtualDatasourceAggregationType, required=False)

    # TODO DELETE: This line can be removed once all clients are migrated
    datasource_type = EnumProperty(DatasourceType, name="datasourceType")

    def __eq__(self, other):
        if isinstance(other, Channel):
            if (self.id != other.id or
                    self.name != other.name or
                    self.description != other.description or
                    self.classifier != other.classifier or
                    self.is_source != other.is_source):
                return False
            if ((self.unit_type is None and other.unit_type is not None) or
                    (self.unit_type is not None and other.unit_type is None)):
                return False
            if (self.unit_type is not None and other.unit_type is not None and
                    self.unit_type.name != other.unit_type.name):
                return False
            if ((self.datapoint_type is None and other.datapoint_type is not None) or
                    (self.datapoint_type is not None and other.datapoint_type is None)):
                return False
            if (self.datapoint_type is not None and other.datapoint_type is not None and
                    self.datapoint_type.name != other.datapoint_type.name):
                return False
            if ((self.aggregation_type is None and other.aggregation_type is not None) or
                    (self.aggregation_type is not None and other.aggregation_type is None)):
                return False
            if (self.aggregation_type is not None and other.aggregation_type is not None and
                    self.aggregation_type.name != other.aggregation_type.name):
                return False
            return True
        else:
            return False


class Datasource(EnergyworxDomain):
    channels = StructuredProperty(Channel, name="channels", repeated=True)
    tags = StructuredProperty(Tag, name="tags", repeated=True)
    name = Property(name="name", required=True)
    description = Property(name="description", required=False, default="No description")
    timezone = Property(name="timezone", required=False)
    filter = Property(name="filter", required=False)
    limit = Property(name="limit")
    more = Property(name="more")
    updated_datetime = Property(name="updatedDatetime")
    created_datetime = Property(name="createdDatetime")
    classifier = Property(name="classifier", required=False)

    def get_channel_by_id(self, channel_id):
        for channel in self.channels:
            if channel.id == channel_id:
                return channel

    def get_channel_by_classifier(self, channel_classifier):
        for channel in self.channels:
            if channel.classifier == channel_classifier:

                return channel

    def get_source_channels(self):
        for channel in self.channels:
            if channel.is_source:
                yield channel

    def get_tag(self, tag_name, latest_version=False, active_versions=False, all_versions=False):
        """ Get the tag with name tag_id. You have the option to select
        the latest version, the active versions and/or all versions. A
        tuple with three values will always be returned, however, only
        the parameters with value True will actually return the wanted
        tags. The order of the return values in the returned tuple is:
        latest_version, active_versions, all_versions.

        Args:
            tag_name (str): Name of the tag to be retrieved
            latest_version (bool):
            active_versions (bool):
            all_versions (bool):

        Returns:

            tuple[Tag, list[Tag], list[Tag]]: if a list of tags is returned,
                the list is sorted in asceding order based on tag.version
        """
        corresponding_tags = filter(lambda tag: tag.tag == tag_name, self.tags)  # type: Union[str, unicode, Tuple[Any, ...], List[Any]]
        if not corresponding_tags:
            # no tags found for tag_name
            logger.warn("No tag found for name: %s", tag_name)
            return None, [], []
        # sort the tags based on the version attribute in ascending order
        corresponding_tags = sorted(corresponding_tags, key=operator.attrgetter('version'), reverse=False)
        # prepare latest version response
        latest_version_result = None
        if latest_version:
            latest_version_result = corresponding_tags[-1]
        # prepare active versions response
        active_versions_result = []
        if active_versions:
            # filters out any tag versions that are overruled in the SCD timeline
            valid_froms = [t.valid_from for t in corresponding_tags]
            active_versions_result = []
            latest_active_valid_from = datetime(3000, 1, 1, 1, tzinfo=pytz.UTC)
            for idx in range(-1, -(len(valid_froms) + 1), -1):
                valid_from = valid_froms[idx]
                if valid_from < latest_active_valid_from:
                    # prepend the tag to get a list of tags in ascending order (based on version)
                    active_versions_result.insert(0, corresponding_tags[idx])
                    latest_active_valid_from = valid_from
        # prepare all versions response
        all_versions_result = []
        if all_versions:
            all_versions_result = corresponding_tags
        return latest_version_result, active_versions_result, all_versions_result

    def cache_compare(self, cache_datasource):
        """
        Only compare the available channels and tags against cached datasource ignore channels that are available
        in cached datasource that are not available in this instance
        """
        return cache_datasource is not None and all([cache_datasource is not None,
                                                     self.id == cache_datasource.id,
                                                     self.name == cache_datasource.name,
                                                     self.description == cache_datasource.description,
                                                     self.classifier == cache_datasource.classifier,
                                                     self.timezone == cache_datasource.timezone,
                                                     self.filter == cache_datasource.filter,
                                                     all([channel == cache_datasource.get_channel_by_id(channel.id) for channel in self.channels]),
                                                     all([any([tag == version for version in cache_datasource.get_tag(tag.tag, all_versions=True)[2]]) for tag in self.tags])])

    def __eq__(self, other):
        if isinstance(other, Datasource):
            if (self.id != other.id or
                    self.name != other.name or
                    self.description != other.description or
                    self.classifier != other.classifier or
                    self.timezone != other.timezone):
                return False
            if len(self.tags) != len(other.tags):
                return False
            for _tag in self.tags:
                if _tag not in other.tags:
                    return False
            if len(self.channels) != len(other.channels):
                return False
            for _channel in self.channels:
                if _channel not in other.channels:
                    return False
            return True
        else:
            return False


class TimeseriesSet:
    def __init__(self, datasource_id, channel_classifier_id, start_timestamp, end_timestamp):
        self.datasource_id = datasource_id
        self.channel_classifier_id = channel_classifier_id
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp


class PrepareContext:
    def __init__(self, timeseries_sets):
        self.timeseries_sets = timeseries_sets


class Timeslice(EnergyworxDomain):
    period_type = EnumProperty(TimeslicePeriodType, name='periodType')
    priority = Property(name='priority')
    starts = Property(name='starts', repeated=True)
    ends = Property(name='ends', repeated=True)
    value = Property(name='value')


class TimesliceGroup(EnergyworxDomain):
    name = Property(name='name')
    description = Property(name='description')
    properties = StructuredProperty(KeyValueType, name='properties', repeated=True)
    timeslices = StructuredProperty(Timeslice, name='timeslices', repeated=True)
