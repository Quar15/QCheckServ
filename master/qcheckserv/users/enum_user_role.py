from enum import Enum

class EnumUserRole(Enum):

    USER = 0
    ADMIN = 1


    def __repr__(self):
        return self.value


    def __str__(self):
        return f"{self.value}"