from .core import ConverterManager as ConvMan
from .core import BaseConverter

ConverterManager = None

def load(file_path):
    global ConverterManager
    ConverterManager = ConvMan(file_path)


__all__ = [
    'ConverterManager',
    'BaseConverter',
]