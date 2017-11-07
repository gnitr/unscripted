from .thing import Thing, ThingParentError
from random import random
import math

class World(Thing):
    '''
    
    '''
    def __init__(self, **kwargs):
        defaults = {
            'dims': [100.0] * 3,
            'capacity': {
                'bot': 10,
                'thing': 100,
            }
        }
        defaults['pos'] = [defaults['dims'][0] / 2, 0, defaults['dims'][2] / 2]
        defaults.update(kwargs)
        super(World, self).__init__(**defaults)
    
    def walk(self, actor, angle=0.0):
        step_size = 0.5
        angle_radian = float(angle) * math.pi * 2
        
        pos = actor.pos
        actor.pos[0] = pos[0] + math.cos(angle_radian) * step_size
        actor.pos[2] = pos[2] + math.sin(angle_radian) * step_size
        
        if actor.is_position_valid():
            actor.save()
        else:
            actor.pos = pos

    def get_random_pos(self):
        return [random() * self.dims[0], 0, random() * self.dims[2]]
    
    def _before_inserting_child(self, child):
        cache = []
        while True:
            child.pos = self.get_random_pos()
            if child.is_position_valid(cache):
                break
        
        # TODO: move capacity quota to Thing
        
        for module_key, quantity in self.capacity.iteritems():
            module_class = self.get_class_from_module_key(module_key)
            if isinstance(child, module_class):
                # TODO: we need to get all subclasses as well!
                filter = {'parentid': self.pk}
                if module_key != 'thing':
                    filter['module'] = module_key
                c = Thing.objects.filter(**filter).count()
                if c >= quantity:
                    raise ThingParentError('This world cannot accept more than %s %s.' % (quantity, module_key))

    def _before_changing_parent(self):
        if self.parentid:
            raise ThingParentError('Cannot move World X inside something else')

