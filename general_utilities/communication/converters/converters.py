from .core import BaseConverter
from enum import IntEnum


class B1Converter(BaseConverter):
    datapoint_types = [
        'DPT_Switch',
        'DPT_Bool',
        'DPT_Enable',
        'DPT_Ramp',
        'DPT_Alarm',
        'DPT_BinaryValue',
        'DPT_Step',
        'DPT_UpDown',
        'DPT_OpenClose',
        'DPT_Start',
        'DPT_State',
        'DPT_Invert',
        'DPT_DimSendStyle',
        'DPT_InputSource',
        'DPT_Reset',
        'DPT_Ack',
        'DPT_Trigger',
        'DPT_Occupancy',
        'DPT_Window_Door',
        'DPT_LogicalFunction',
        'DPT_Scene_AB',
        'DPT_ShutterBlinds_Mode',
    ]

    bit_size = 1

    def __init__(self):
        super().__init__()
        self.data = False

    def write_binary(self, data):
        self.data = bool(data[-1])

    def read_binary(self):
        return int(self.data)

    def write_json(self, data):
        self.data = data['data']

    def read_json(self):
        return {'data': self.data}


class U8Converter(BaseConverter):
    datapoint_types = [
        'DPT_Scaling',
        'DPT_Angle',
        'DPT_Percent_U8',
        'DPT_DecimalFactor',
    ]

    bit_size = 8

    def __init__(self):
        super().__init__()
        self.data = 0

    def write_binary(self, data):
        self.data = data[-1] & 0xFF

    def read_binary(self):
        return self.data

    def write_json(self, data):
        self.data = data['data']

    def read_json(self):
        return {'data': self.data}


class B5Converter(BaseConverter):
    datapoint_types = [
        'DPT_Custom_HagerStatus'
    ]

    bit_size = 5

    class Position(IntEnum):
        MIDDLE = 0
        TOP = 1
        BOTTOM = 2
    
    class OperatingMode(IntEnum):
        NORMAL = 0
        PRIORITY = 1
        ALARM_WIND = 2
        ALARM_RAIN = 3
        DISABLED = 4

    def __init__(self):
        super().__init__()
        self.data_position = B5Converter.Position.MIDDLE
        self.data_mode = B5Converter.OperatingMode.NORMAL

    def write_binary(self, data):
        data = data[-1] & 0x1F
        self.data_position = B5Converter.Position(data & 0b11)
        self.data_mode = B5Converter.OperatingMode((data & 0b111) >> 3)


    def read_binary(self):
        data = (self.data_mode << 3) & self.data_position
        return data

    def write_json(self, data):
        pos = data['data_position']
        mode = data['data_mode']
        self.data_position = B5Converter.Position.__dict__[pos]
        self.data_mode = B5Converter.OperatingMode.__dict__[mode]

    def read_json(self):
        return {'data_position': self.data_position.name, 'data_mode': self.data_mode.name}
