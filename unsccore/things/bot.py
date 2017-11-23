from .thing import Thing

class Bot(Thing):
    '''
    A Bot
    '''

    def __init__(self, **kwargs):
        # last valid parentid value
        noname = 'noname'
        defaults = {
            'dims': (0.5, 1.7, 0.3),
            'drink_': 1.0,
            'action_count': 0,
            'generation': 0,
            'name': noname,
            'female': 0,
        }
        defaults.update(kwargs)
        super(Bot, self).__init__(**defaults)
        
        if self.name == noname:
            import names
            self.name = names.get_first_name(gender='female' if self.female else 'male')
    
    def drink(self):
        self.drink_ = 1.0
        
    def after_action(self):
        ret = True
        
        self.action_count += 1
        # Real walking speed = 5 km/h
        # Real walking step size = 0.8m
        # If resolution of action is a walking step
        # we have 6250 actions per hour
        # or 104 / minutes 
        # or 1.7 steps/cycle per second
        # => 1 cycle ~= 0.6 seconds to be real time
        # B bots * 1 action / cycle => ~ 2 x B actions / seconds
        # 150k actions / bot / day
        cycles_in_a_day = 5000.0/0.8*24
        # 1 day without drinking and dies
        self.drink_ -= 1.0 / cycles_in_a_day
        #print self.action_count
        # 10 days lifespan
        if self.action_count < 10*cycles_in_a_day:
            #self.save()
            pass
        else:
            ret = self.die('natural')
        
        if ret and self.drink_ < 0.0:
            ret = self.die('thirst')
            
        return ret

    def die(self, cause='unknown'):
        print 'DIE of %s' % cause
        self.delete()
        return False
        