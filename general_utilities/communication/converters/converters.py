from .core import BaseConverter


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
