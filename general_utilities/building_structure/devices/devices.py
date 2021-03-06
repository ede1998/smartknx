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


class Garage(Device):
    yaml_tag = u'!Garage'
    template = 'smartknx/card_garage.html'

    def __init__(self, read_top, read_bottom, write_stop, name='Garage'):
        super().__init__(name)
        self.write_stop = get_group_address_converter(write_stop, 'DPT_Start')
        self.read_top = get_group_address_converter(read_top, 'DPT_Bool')
        self.read_bottom = get_group_address_converter(read_bottom, 'DPT_Bool')


class Blind(Device):
    yaml_tag = u'!Blind'
    template = 'smartknx/card_blind.html'

    def __init__(self, read_position, write_position, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_position = get_group_address_converter(read_position, 'DPT_Scaling')
        self.write_position = get_group_address_converter(write_position, 'DPT_Scaling')
        self.write_direction = get_group_address_converter(write_direction, 'DPT_Switch')
        self.write_stop = get_group_address_converter(write_stop, 'DPT_Start')


class Dimmer(Device):
    yaml_tag = u'!Dimmer'
    template = 'smartknx/card_dimmer.html'

    def __init__(self, read, write, write_position, read_position, name='Dimmer'):
        super().__init__(name)
        self.read = get_group_address_converter(read, 'DPT_Switch')
        self.write = get_group_address_converter(write, 'DPT_Switch')
        self.write_position = get_group_address_converter(write_position, 'DPT_Scaling')
        self.read_position = get_group_address_converter(read_position, 'DPT_Scaling')

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r, write_position=%r, read_position=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write, self.write_position, self.read_position)
