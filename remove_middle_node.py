import yaml

test_str="""!test
test:
  !abc
  name: abc"""

def const(loader, node):
  m = loader.construct_mapping(node)
  print(m)
  return m['test']

class Abc(yaml.YAMLObject):
  yaml_tag = '!abc'

yaml.add_constructor('!test', const)

doc = yaml.load(test_str)
