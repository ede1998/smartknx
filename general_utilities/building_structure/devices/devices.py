from .core import Device
from ...communication.converters import *


class Light(Device):
    yaml_tag = u'!Light'
    template = 'smartknx/card_light.html'

    def __init__(self, write, read, name='Light'):
        super().__init__(name)
        self.read = ConverterManager.get_converter(read, 'DPT_Switch')
        self.write = ConverterManager.get_converter(write, 'DPT_Switch')

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write)


class Outlet(Device):
    yaml_tag = u'!Outlet'
    template = 'smartknx/card_outlet.html'

    def __init__(self, read, write, name='Outlet'):
        super().__init__(name)
        self.read = ConverterManager.get_converter(read, 'DPT_Switch')
        self.write = ConverterManager.get_converter(write, 'DPT_Switch')

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write)


class BlindOld(Device):
    yaml_tag = u'!BlindOld'
    template = 'smartknx/card_blind_old.html'

    def __init__(self, read_top, read_bottom, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_top = ConverterManager.get_converter(read_top, 'DPT_Bool')
        self.read_bottom = ConverterManager.get_converter(
            read_bottom, 'DPT_Bool')
        self.write_direction = ConverterManager.get_converter(
            write_direction, 'DPT_Switch')
        self.write_stop = ConverterManager.get_converter(
            write_stop, 'DPT_Start')


#class GarageDoor(BlindOld):
    #def __init__(self, name='Garage'):
        #super().__init__(name)


class Blind(Device):
    yaml_tag = u'!Blind'
    template = 'smartknx/card_blind.html'

    def __init__(self, read_position, write_position, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_position = ConverterManager.get_converter(
            read_position, 'DPT_Scaling')
        self.write_direction = ConverterManager.get_converter(
            write_direction, 'DPT_Switch')
        self.write_stop = ConverterManager.get_converter(
            write_stop, 'DPT_Start')
