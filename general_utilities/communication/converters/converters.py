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

    def write_binary(self, data):
        self._data_binary = data
        self._data_json = bool(data)
        self.data = bool(data)

    def read_binary(self):
        return self._data_binary

    def write_json(self, data):
        self._data_json = data
        self._data_binary = int(data)
        self.data = data

    def read_json(self):
        return self._data_json


class U8Converter(BaseConverter):
    datapoint_types = [
        'DPT_Scaling',
        'DPT_Angle',
        'DPT_Percent_U8',
        'DPT_DecimalFactor',
    ]

    def write_binary(self, data):
        self._data_binary = data
        self._data_json = data[0] & 0xFF
        self.data = self._data_json

    def read_binary(self):
        return self._data_binary

    def write_json(self, data):
        self._data_json = data
        self._data_binary = data
        self.data = data

    def read_json(self):
        return self._data_json
