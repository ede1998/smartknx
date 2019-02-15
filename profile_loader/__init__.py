from .container import *
from .objects import *
from .group_address import *
import oyaml as yaml

def load(path):
    f = open(path, 'r')
    return yaml.load(f)
