from .group_address import GroupAddress
from enum import Enum, auto
import json


class Type(Enum):
    UNKOWN = auto()
    B1 = auto()
    B1U3 = auto()
    U8 = auto()
    F16 = auto()


class KNXMessage:
    group_address_translator = dict()

    def __init__(self, group_address, typ):
        super().__init__()
        assert isinstance(group_address, GroupAddress), "GroupAddress expected, got %s: %s" % (type(group_address).__name__, str(group_address))
        assert isinstance(typ, Type)
        self.group_address = group_address
        self.type = typ
        self.data = None
        KNXMessage.group_address_translator[str(group_address)] = self

    def __repr__(self):
        return "KNXMessage(group_address=%s, type=%s, data=%s)" % (
            self.group_address, self.type, self.data)
    
    @staticmethod
    def get_group_type(group_address):
        msg = KNXMessage.group_address_translator.get(str(group_address))
        if msg is None:
            return Type.UNKOWN
        else:
            return msg.type

    def convert_data(self, to_python):
        if to_python:
            self._convert_data_to_python()
        else:
            self._convert_data_to_binary()

    def _convert_data_to_python(self):
        data_old = self.data
        if self.type is Type.B1:
            self.data = bool(data_old[-1])
        elif self.type is Type.B1U3:
            self.data = (
                bool((data_old[-1] & 0b1000) >> 3), data_old[-1] & 0b111)
        elif self.type is Type.U8:
            self.data = data_old[0] & 0xFF
        elif self.type is Type.F16:
            M = ((data_old[-2] & 0b111) << 8) + (data_old[-1] & 0xFF)
            M = -M if data_old[-2] & (1 << 7) else M
            E = (data_old[-2] & 0x78) >> 3
            self.data = float(0.01*M * (2**E))

    def _convert_data_to_binary(self):
        data_old = self.data
        if self.type is Type.B1:
            self.data = int(data_old)
        elif self.type is Type.B1U3:
            self.data = int(data_old[0]) << 3 | data_old[1]
        elif self.type is Type.U8:
            pass
        elif self.type is Type.F16:
            data_old *= 100.0
            E = 0
            while not (-2048 <= data_old < 2047):
                E += 1
                data_old /= 2.0
            assert(0 <= E <= 15)
            sign = 1 if data_old < 0 else 0
            M = int(abs(data_old))
            self.data = [sign << 7 | E << 3 | M >> 8, M & 0xFF]

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
    def unserialize_json(cls, string):
        try:
            o = json.loads(string)
        except json.JSONDecodeError as e:
            print(e)
            return None
        addr = map(int, o['group_address'].split('/'))
        addr = GroupAddress(*addr)
        typ = Type[o['type']]
        instance = cls(addr, typ)
        instance.data = o['data']
        return instance

    def serialize_redis(self):
        d = self.data
        self.convert_data(False)
        ret = self.data
        self.data = d
        return str(self.group_address), ret

    @classmethod
    def unserialize_redis(cls, group_address, data, typ):
        assert isinstance(group_address, str)
        assert isinstance(data, str)
        addr = GroupAddress(*map(int, group_address.split('/')))
        o = KNXMessage(addr, typ)
        o.data = json.loads(data)
        o.convert_data(True)
        return o
    