import oyaml as yaml


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

class ConverterFactory:
    def __init__(self, config_file_name):
        self.converters = dict()
        self._load_config(config_file_name)

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
