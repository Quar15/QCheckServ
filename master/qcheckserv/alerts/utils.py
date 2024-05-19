from enum import Enum


class EnumTriggerTypeEnum(Enum):
    STATUS = 0
    PERCENTAGE_USAGE = 1
    STORAGE = 2
    LOAD_AVG = 3
    NETWORK = 4


class EnumAlertTriggerTypeComparator(Enum):
    DEFAULT = 0
    BIGGER = 1
    BIGGER_EQUAL = 2
    LESS = 3
    LESS_EQUAL = 4
    EQUAL = 5


class EnumAlertNotificationType(Enum):
    RSYSLOG = 0
    HTTP_REQUEST = 1
    MAIL = 2


class EnumAlertStatus(Enum):
    NEW = 0
    WAITING = 1
    ACTIVE = 2
    ENDED = 3
    ACKNOWLEDGED = 4
