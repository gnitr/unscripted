from .thing import Thing

class Bot(Thing):
    '''
    A Bot
    '''

    def __init__(self, **kwargs):
        # last valid parentid value
        defaults = {
            'dims': (0.5, 1.7, 0.3),
        }
        defaults.update(kwargs)
        super(Bot, self).__init__(**defaults)
        
    def observe(self, actor):
        pass