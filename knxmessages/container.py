import oyaml as yaml

class Container(yaml.YAMLObject):
    yaml_tag = u'!Container'

    def __init__(self, name, children):
        super().__init__()
        self.name = name
        self.children = children
    
    def __repr__(self):
        return '{ name: ' + self.name + ', children: ' + repr(self.children) + '}'
    
    def __str__(self):
        return 'Containername: ' + self.name + '\n' + str(self.children)