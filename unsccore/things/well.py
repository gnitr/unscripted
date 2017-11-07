from .thing import Thing

class Well(Thing):
    '''
    A Well full of drinkable water
    '''

    def __init__(self, **kwargs):
        # last valid parentid value
        defaults = {
            'dims': (1.0, 1.0, 1.0),
        }
        defaults.update(kwargs)
        super(Well, self).__init__(**defaults)
    
    def drink(self, actor):
        actor.drink()
