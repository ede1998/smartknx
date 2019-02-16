import itertools
import oyaml as yaml  # make sure order in yaml file is preserved
from .knx_message import KNXMessage, Type


class Object(yaml.YAMLObject):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return "%s(name=%r)" % (self.__class__.__name__, self.name)


class Light(Object):
    yaml_tag = u'!Light'

    def __init__(self, write, read, name='Light'):
        super().__init__(name)
        self.read = KNXMessage(read, Type.BOOLEAN)
        self.write = KNXMessage(write, Type.BOOLEAN)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node))

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write)


class Outlet(Object):
    yaml_tag = u'!Outlet'

    def __init__(self, read, write, name='Outlet'):
        super().__init__(name)
        self.read = KNXMessage(read, Type.BOOLEAN)
        self.write = KNXMessage(write, Type.BOOLEAN)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node))

    def __repr__(self):
        return "%s(name=%r, read=%r, write=%r)" % (
            self.__class__.__name__, self.name, self.read, self.write)


class BlindOld(Object):
    yaml_tag = u'!BlindOld'

    def __init__(self, read_top, read_bottom, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_top = KNXMessage(read_top, Type.BOOLEAN)
        self.read_bottom = KNXMessage(read_bottom, Type.BOOLEAN)
        self.write_direction = KNXMessage(write_direction, Type.BYTE)
        self.write_stop = KNXMessage(write_stop, Type.BOOLEAN)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node))

#class GarageDoor(BlindOld):
    #def __init__(self, name='Garage'):
        #super().__init__(name)


class Blind(Object):
    yaml_tag = u'!Blind'

    def __init__(self, read_position, write_position, write_direction, write_stop, name='Blinds'):
        super().__init__(name)
        self.read_position = KNXMessage(read_position, Type.BYTE)
        self.write_position = KNXMessage(write_position, Type.BYTE)
        self.write_direction = KNXMessage(write_direction, Type.BYTE)
        self.write_stop = KNXMessage(write_stop, Type.BOOLEAN)

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node))


_path_objects = ['floors', None,
                 'rooms', None,
                 'devices', None]

# remove types: Light, Blind, ...
yaml.add_constructor('!device', lambda loader, node:
                     list(loader.construct_mapping(node).values())[0])
yaml.add_path_resolver('!device', _path_objects)

for subclass in Object.__subclasses__():
    yaml.add_path_resolver(subclass.__dict__['yaml_tag'],
                           itertools.chain(_path_objects, [subclass.__name__]))
