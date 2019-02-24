import oyaml as yaml
import json


class BaseConverter:

    def get_binary(self):
        return self.read_binary()

    def set_binary(self, data):
        self.write_binary(data)

    def get_json(self):
        return self.read_json()

    def set_json(self, data):
        self.write_json(data)

    data_json = property(get_json, set_json)
    data_binary = property(get_binary, set_binary)

from . import converters

class ConverterManager:
    def __init__(self, config_file_name):
        self.converters = dict()
        self._load_config(config_file_name)
    
    def serialize_json(self, group_address):
        json_dict = self.converters[group_address].data_json
        json_dict['group_address'] = group_address
        return json.dumps(json_dict)
    
    def unserialize_json(self, msg):
        json_dict = json.loads(msg)
        group_address = json_dict.pop('group_address')
        self.converters[group_address].data_json = json_dict
        return group_address, self.converters[group_address]

    def serialize_binary(self, group_address):
        return self.converters[group_address].data_binary
    
    def unserialize_binary(self, group_address, data):
        # redis returns a string to us, knxmap sent out an array
        assert(isinstance(data, str))
        data = json.loads(data)
        self.converters[group_address].data_binary = data
        return group_address, self.converters[group_address]

    def _load_config(self, yaml_file):
        with open(yaml_file, 'r') as file:
            config = yaml.safe_load(file)
            for group_address, group_type in config.items():
                print(group_address + "  " + group_type)
                converter = self._create_instance(group_address, group_type)
                if converter is None:
                    print('Unknown converter for "%s" at group address %s. Correct datapoint type or write your own converter.' % (
                        group_type, group_address))
                else:
                    self.converters[group_address] = converter

    def _create_instance(self, group_address, group_type):
        for converter in BaseConverter.__subclasses__():
            if group_type in converter.datapoint_types:
                return converter()
        return None
