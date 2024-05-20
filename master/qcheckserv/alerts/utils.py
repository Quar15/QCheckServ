from enum import IntEnum, Enum


class EnumTriggerTypeEnum(IntEnum):
    STATUS = 0
    PERCENTAGE_USAGE = 1
    STORAGE = 2
    LOAD_AVG = 3
    NETWORK = 4


class EnumAlertTriggerTypeComparator(IntEnum):
    BIGGER = 0
    BIGGER_EQUAL = 1
    LESS = 2
    LESS_EQUAL = 3
    EQUAL = 4


class EnumAlertNotificationType(IntEnum):
    RSYSLOG = 0
    HTTP_REQUEST = 1
    MAIL = 2


class EnumAlertStatus(IntEnum):
    NEW = 0
    WAITING = 1
    ACTIVE = 2
    ENDED = 3
    ACKNOWLEDGED = 4


class EnumServerResourceType(Enum):
    CPU_PERC = 'cpu_perc'
    MEM_PERC = 'mem_perc'


class EnumStorageResourceType(Enum):
    INODES_PERC = 'inodes_perc'
    USAGE_PERC = 'usage_perc'
    USED = 'used'


class EnumNetworkResourceType(Enum):
    UPLOAD = 'upload'
    DOWNLOAD = 'download'