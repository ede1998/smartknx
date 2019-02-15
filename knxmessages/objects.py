import itertools
import oyaml as yaml # make sure order in yaml file is preserved


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
        self.read = read
        self.write = write

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
        self.read = read
        self.write = write

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
        self.read_top = read_top
        self.read_bottom = read_bottom
        self.write_direction = write_direction
        self.write_stop = write_stop

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
        self.read_position = read_position
        self.write_position = write_position
        self.write_direction = write_direction
        self.write_stop = write_stop

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node))


_path_objects = ['buildings', None,
                 'floors', None,
                 'rooms', None,
                 'devices', None]

# remove types: Light, Blind, ...
yaml.add_constructor('!device', lambda loader, node:
                     list(loader.construct_mapping(node).values())[0])
yaml.add_path_resolver('!device', _path_objects)

for subclass in Object.__subclasses__():
    yaml.add_path_resolver(subclass.__dict__['yaml_tag'],
                           itertools.chain(_path_objects, [subclass.__name__]))
