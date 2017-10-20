from .thing import Thing

class World(Thing):
    '''
    
    '''
    def walk(self, actor, angle=0.0):
        actor.move(angle=angle)
        
