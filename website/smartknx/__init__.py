from general_utilities.communication import converters
converters.load('../config/group-address-types.yaml')
from general_utilities import building_structure

configuration = building_structure.load('../config/layout.yaml')

default_app_config = 'smartknx.apps.SmartknxConfig'