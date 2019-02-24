import itertools
import oyaml as yaml  # make sure order in yaml file is preserved


class Device(yaml.YAMLObject):
    def __init__(self, name):
        super().__init__()
        self.name = name

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(**loader.construct_mapping(node))

    def __repr__(self):
        return "%s(name=%r)" % (self.__class__.__name__, self.name)

from . import devices

_path_objects = ['floors', None,
                 'rooms', None,
                 'devices', None]


# remove types:
#     - Light: # <--
#       name: ...
#     - Blind: # <--
#      ...
yaml.add_constructor('!device', lambda loader, node:
                     list(loader.construct_mapping(node).values())[0])
yaml.add_path_resolver('!device', _path_objects)

for subclass in Device.__subclasses__():
    yaml.add_path_resolver(subclass.__dict__['yaml_tag'],
                           itertools.chain(_path_objects, [subclass.__name__]))
