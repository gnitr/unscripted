from .thing import Thing, ThingParentError
from random import random

class World(Thing):
    '''
    
    '''
    def __init__(self, **kwargs):
        defaults = {
            'dims': [100.0] * 3,
        }
        defaults.update(kwargs)
        super(World, self).__init__(**defaults)
    
    def walk(self, actor, angle=0.0):
        actor.move(angle=angle)

    def get_random_pos(self):
        return [dim * random() for dim in self.dims]
    
    def _before_inserting_child(self, child):
        child.pos = self.get_random_pos()
        pass

    def _before_changing_parent(self):
        if self.parentid:
            raise ThingParentError('Cannot move World X inside something else')


