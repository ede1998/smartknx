from .group_address import GroupAddress
from enum import Enum, auto
import json


class Type(Enum):
    BOOLEAN = auto()
    BIT3 = auto()
    BYTE1 = auto()
    BYTE2 = auto()


class KNXMessage:

    def __init__(self, group_address, typ):
        super().__init__()
        self.group_address = group_address
        self.type = typ
        self.data = None

    def __repr__(self):
        return "KNXMessage(group_address=%s, type=%s, data=%s)" % (
            self.group_address, self.type, self.data)

    def __hash__(self):
        return self.group_address.__hash__()

    def serialize_json(self):
        def custom_encoder(o):
            if isinstance(o, KNXMessage):
                return o.__dict__
            elif isinstance(o, Type):
                return o.name
            elif isinstance(o, GroupAddress):
                return str(o)
            else:
                type_name = type(o).__name__
                raise TypeError(
                    f"Object of type '{type_name}' is not JSON serializable")

        return json.dumps(self, default=custom_encoder)

    @classmethod
    def unserialize_json(cls, str):
        o = json.loads(str)
        addr = map(int, o['group_address'].split('/'))
        addr = GroupAddress(*addr)
        typ = Type[o['type']]
        instance = cls(addr, typ)
        instance.data = o['data']
        return instance
