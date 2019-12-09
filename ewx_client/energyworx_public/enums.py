from enum import Enum


class DatasourceType(Enum):
    # Also update list method of ChannelClassifierTypesModel in model.py and the packages/energyworx/energyworx/enum.py
    power = 0
    gas = 1
    water = 2
    annotation = 3
    temperature = 4
    time = 5
    air = 6
    weather = 7
    statistic = 8
    steam = 9
    system = 10


class DatapointType(Enum):
    interval = 0
    register = 1
    gauge = 2
    annotation = 3


class TagType(Enum):
    static = 0
    scd = 1


class VirtualDatasourceAggregationType(Enum):
    sum = 0
    mean = 1
    max = 3
    min = 4
    count = 5


class UnitType(Enum):
    # Also update:
    # -  list method of ChannelClassifierTypesModel in model.py
    # -  UnitType and DataSourceType of domain.py in energyworx_shared package
    # -  enum.py in energyworx package
    kWh = 0
    Wh = 1
    m3 = 2
    mtq = 3
    l = 4
    W = 5
    kW = 6
    C = 7
    F = 8
    perc = 9
    annotation = 10
    seconds = 12
    bar = 13
    mbar = 14
    KVARH = 15
    kVAr = 16
    V = 17
    kV = 18
    mV = 19
    A = 20
    mA = 21
    mps = 22  # meters per second
    degrees = 23  # mathematical angle
    days = 24
    hours = 25
    unit = 26
    permillage = 27
    MWh = 28
    kVA = 29
    KVAH = 30
    gal = 31
    Ohm = 32
    lps = 33
    MW = 34
    mWh = 35
    MVArh = 36
    kVArh = 37
    VArh = 38
    mVArh = 39
    MVAr = 40
    VAr = 41
    mVAr = 42
    kA = 43
    fraction = 44
    factor = 45
    kWt = 46  # Thermal power in kilowatts


class TransformationMapFunctionType(Enum):
    composite = 0
    generate_id = 1
    local_to_utc = 2
    split = 3
    to_date = 4
    to_geopoint = 5
    to_heartbeat = 6


class MappedFieldType(Enum):
    string = 0
    number = 1
    boolean = 2
    enum = 3
    timestamp = 4


class TimeslicePeriodType(Enum):
    dst = 1
    daily = 2
    weekdays = 3
    saturday = 4
    sunday = 5
    holiday = 6
    sunday_holiday = 7
    weekend = 8


class ConsolidationType(Enum):
    sum = 0
    mean = 1
    median = 2
    max = 3
    min = 4
    std = 5
    var = 6
    count = 7
    first = 8
    last = 9

# ENUMS END #


def str_to_enum(enum_cls, str_value, ignore_case=False):
    if str_value:
        if ignore_case:
            for enum_value in enum_cls:
                if enum_value.name.lower() == str(str_value).lower():
                    return enum_value
        else:
            return enum_cls.__dict__[str(str_value)]

