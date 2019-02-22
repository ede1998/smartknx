import re
import oyaml as yaml


class GroupAddress(yaml.YAMLObject):
    yaml_tag = '!GroupAddress'

    def __init__(self, main, middle, sub):
        super().__init__()
        self.main = main
        self.middle = middle
        self.sub = sub

    @classmethod
    def from_yaml(cls, loader, node):
        value = loader.construct_scalar(node)
        main, middle, sub = map(int, value.split('/'))
        return cls(main, middle, sub)

    def __repr__(self):
        return "GroupAddress(main=%i, middle=%i, sub=%i)" % (self.main, self.middle, self.sub)
    
    def __str__(self):
        return "%i/%i/%i" % (self.main, self.middle, self.sub)


_pattern = re.compile(r'^\d{1,2}/\d{1,2}/\d{1,3}$')
yaml.add_implicit_resolver(GroupAddress.yaml_tag, _pattern)
