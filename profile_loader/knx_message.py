from . import group_address as ga
from enum import Enum, auto


class Type(Enum):
    BOOLEAN = auto()
    BYTE = auto()


class KNXMessage:

    def __init__(self, group_address, type):
        super().__init__()
        self.group_address = group_address
        self.type = type
        self.data = None

    def __repr__(self):
        return "KNXMessage(group_address=%s, type=%s, data=%s)" % (
            self.group_address, self.type, self.data)
