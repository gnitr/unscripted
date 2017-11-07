from .thing import Thing

class Bot(Thing):
    '''
    A Bot
    '''

    def __init__(self, **kwargs):
        # last valid parentid value
        defaults = {
            'dims': (0.5, 1.7, 0.3),
            'drink_': 1.0,
            'action_count_': 0,
        }
        defaults.update(kwargs)
        super(Bot, self).__init__(**defaults)
        
    
    def drink(self):
        self.drink = 1.0
        
    def after_action(self):
        ret = True
        
        self.action_count_ += 1
        self.drink_ -= 1.0/60/24
        print self.action_count_
        if self.action_count_ < 10*60*24:
            self.save()
        else:
            ret = self.die('natural')
        
        if ret and self.drink_ < 0.1:
            ret = self.die('thirst')
            
        return ret

    def die(self, cause='unknown'):
        print 'DIE of %s' % cause
        self.delete()
        return False
        