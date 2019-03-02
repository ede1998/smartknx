import itertools
import oyaml as yaml  # make sure order in yaml file is preserved
from ...communication.converters import *
import logging

LOGGER = logging.getLogger(__name__)

def get_converter(group_address, datapoint_type=None):
   try:
        converter = ConverterManager.converters[group_address]
   except KeyError as e:
        raise RuntimeError('Group address %s does not exist. Please add it to your configuration file.' % (
            group_address)) from e
   else:
        if not datapoint_type is None:
            if not datapoint_type in converter.datapoint_types:
                raise RuntimeError('Datapoint Type mismatch: %s required, but got %s' % (
                    datapoint_type, converter.datapoint_types))
        return converter


def get_group_address_converter(group_address, datapoint_type):
    converter = get_converter(group_address, datapoint_type)
    return {'group_address': group_address, 'converter': converter}


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
