from .container import *
from .devices import *
import oyaml as yaml

def load(path):
    f = open(path, 'r')
    return yaml.load(f)
