
class Object:
    def __init__(self, name):
        super().__init__()
        self.name = name
        
    def __repr__(self):
        return '{ type: ' + str(type(self)) + ', name: ' + self.name + ' }'
    
class OnOff(Object):
    address_read = None
    address_write = None
    
class Light(OnOff):
    def __init__(self, name='Light'):
        super().__init__(name)

class Outlet(OnOff):
    def __init__(self, name='Outlet'):
        super().__init__(name)
        
class BlindOld():
    def __init__(self, name='Blinds'):
        super().__init__(name)

    address_read_top = None
    address_read_bottom = None
    address_write_direction = None
    address_write_stop = None

class GarageDoor(BlindOld):
    def __init__(self, name='Garage'):
        super().__init__(name)
        
class Blind():
    def __init__(self, name='Blinds'):
        super().__init__(name)
    
    address_read_position = None
    address_write_direction = None
    address_write_stop = None