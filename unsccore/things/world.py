from .thing import Thing, ThingParentError
from random import random

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
        defaults.update(kwargs)
        super(World, self).__init__(**defaults)
    
    def walk(self, actor, angle=0.0):
        actor.move(angle=angle)

    def get_random_pos(self):
        return [random() * self.dims[0], 0, random() * self.dims[2]]
    
    def _before_inserting_child(self, child):
        child.pos = self.get_random_pos()
        
        for module_key, quantity in self.capacity.iteritems():
            module_class = self.get_class_from_module_key(module_key)
            if isinstance(child, module_class):
                # TODO: we need to get all subclasses as well!
                filter = {}
                if module_key != 'thing':
                    filter['module'] = module_key
                c = self.objects.filter(**filter).count()
                if c >= quantity:
                    raise ThingParentError('This world cannot accept more than %s %s.' % (quantity, module_key))

    def _before_changing_parent(self):
        if self.parentid:
            raise ThingParentError('Cannot move World X inside something else')


