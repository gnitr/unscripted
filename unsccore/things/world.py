from .thing import Thing
from random import random

class World(Thing):
    '''
    
    '''
    def __init__(self, **kwargs):
        self.dims = [100.0] * 3
        super(World, self).__init__(**kwargs)
    
    def walk(self, actor, angle=0.0):
        actor.move(angle=angle)
        

    def add_thing(self, thing):
        thing.parentid = self.pk
        thing.pos = self.get_random_pos()
        thing.save()
    
    def get_random_pos(self):
        return [dim * random() for dim in self.dims]