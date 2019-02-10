
class Container:
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.children = []
    
    def __repr__(self):
        return '{ name: ' + self.name + ', children: ' + repr(self.children) + '}'
    
    def __str__(self):
        return 'Containername: ' + self.name + '\n' + str(self.children)