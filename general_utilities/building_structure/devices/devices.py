from .core import Device, get_group_address_converter


class Light(Device):
    yaml_tag = u'!Light'
    template = 'smartknx/card_light.html'

    def __init__(self, write, read, name='Light'):
        super().__init__(name)
        self.read = get_group_address_converter(read, 'DPT_Switch')
        self.write = get_group_address_converter(write, 'DPT_Switch')

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write)


class Outlet(Device):
    yaml_tag = u'!Outlet'
    template = 'smartknx/card_outlet.html'

    def __init__(self, read, write, name='Outlet'):
        super().__init__(name)
        self.read = get_group_address_converter(read, 'DPT_Switch')
        self.write = get_group_address_converter(write, 'DPT_Switch')

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write)


class BlindOld(Device):
    yaml_tag = u'!BlindOld'
    template = 'smartknx/card_blind_old.html'

    def __init__(self, read_position, write_position, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_position = get_group_address_converter(read_position, 'DPT_Custom_HagerStatus')
        self.write_position = get_group_address_converter(write_position, 'DPT_Scaling')
        self.write_direction = get_group_address_converter(write_direction, 'DPT_Switch')
        self.write_stop = get_group_address_converter(write_stop, 'DPT_Start')


#class GarageDoor(BlindOld):
    #def __init__(self, name='Garage'):
        #super().__init__(name)


class Blind(Device):
    yaml_tag = u'!Blind'
    template = 'smartknx/card_blind.html'

    def __init__(self, read_position, write_position, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_position = get_group_address_converter(read_position, 'DPT_Scaling')
        self.write_direction = get_group_address_converter(write_direction, 'DPT_Switch')
        self.write_stop = get_group_address_converter(write_stop, 'DPT_Start')
