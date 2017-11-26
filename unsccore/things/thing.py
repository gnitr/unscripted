from unsccore import mogels
from bson.objectid import ObjectId
from django.core.cache import cache
from unsccore.dbackends.utils import ClassProperty
import json

class ThingParentError(Exception):
    pass

class Thing(mogels.MongoDocumentModule):
    '''
    A Thing is an abstract ancestor class to all things in the virtual world.
    
    It introduces fields common to all things:
        pos: the thing's position as 3d vector 
        dims: the thing's dimensions as 3d vector
        parentid: the pk of the thing that contains it
    '''
    
    class Meta:
        db_table = 'things'

    def __init__(self, **kwargs):
        # last valid parentid value
        self._parentid_valid = 1
        defaults = {
            'pos': [0.0] * 3,
            'dims': [1.0] * 3,
            'parentid': None,
            'rootid': None,
        }
        defaults.update(kwargs)
        super(Thing, self).__init__(**defaults)
        if self.pk:
            self._parentid_valid = self.parentid
    
    def spprint(self):
        #print self._get_doc()
        ret = '# %s %s <%s|%s> (%s, %s, %s)' % (
            self.pk,
            self.created,
            self.__class__.__name__, self.module,
            self.pos[0], self.pos[1], self.pos[2],
        )
        return ret
    
    def _set_doc(self, doc):
        super(Thing, self)._set_doc(doc)
        self.parentid = str(doc['parentid']) if doc['parentid'] else None

    def _get_doc(self):
        ret = super(Thing, self)._get_doc()
        ret['parentid'] = ObjectId(self.parentid) if self.parentid else None
        return ret
    
    @classmethod
    def get_objects(cls):
        ret = super(Thing, cls).get_objects()
        if cls == Thing:
            # It's a way to clear the filter module=cls
            # so searching with Thing.objects returns all types of things.
            ret.reset_query()
        return ret

    objects = ClassProperty(get_objects)
    
    def get_parent(self):
        return Thing.objects.get(pk=self.parentid) if self.parentid else None
        
    def set_parent(self, parent=None):
        self.parentid = parent.pk if parent else None

    parent = property(get_parent, set_parent)
    
    def save(self):
        if self.parentid != self._parentid_valid:
            self._before_changing_parent()
        
        super(Thing, self).save()
        
        if self.rootid is None:
            # a new root/world is created, we need to set its .rootid = .id
            self.rootid = self.pk
            # and save again
            super(Thing, self).save()
        
        self._parentid_valid = self.parentid
        
    def _before_changing_parent(self):
        if self.parentid:
            parent = self.parent
            parent._before_inserting_child(self)
            
            self.rootid = parent.rootid
                
        if self.__class__ == Thing:
            raise ThingParentError('Generic Things cannot be added. Please add specific things.')
    
    def _before_inserting_child(self, child):
        raise ThingParentError('Y refuses insertion of child X')

    def get_children(self):
        return Thing.objects.filter(parentid=self.pk)

    def empty(self):
        return self.delete_children()

    def delete_children(self):
        for thing in self.get_children():
            thing.delete()
    
    def delete(self):
        # A in B in C
        # Delete B
        # => A in C
        # TODO: deal with children and parents
        self.delete_children()
        
        super(Thing, self).delete()

    def add_thing(self, thing):
        thing.parentid = self.pk
        thing.save()
    
    def get_bounding_box(self):
        ret = [[], []]
        
        ret[0] = [self.pos[0] - self.dims[0] / 2, self.pos[1], self.pos[2] - self.dims[2] / 2]
        ret[1] = [self.pos[0] + self.dims[0] / 2, self.pos[1] + self.dims[1], self.pos[2] + self.dims[2] / 2]
        
        return ret

    def is_position_valid(self, cache=None):
        ret = False
        obstructing_things = self.get_obstructing_things(cache, True)
        
        if not obstructing_things:
            parent = self.parent
            min0, max0 = self.get_bounding_box()
            min1, max1 = parent.get_bounding_box()
            if (min1[0] < min0[0] and min1[2] < min0[2] and max1[0] > max0[0] and max1[2] > max0[2]):
                ret = True
                
        return ret

    def get_obstructing_things(self, cache=None, first_only=False, gap=0.0):
        ret = []
        # TODO: optimse this! And don't fetch everything from DB!
        min0, max0 = self.get_bounding_box()
        if gap:
            min0[0] -= gap
            min0[2] -= gap
            max0[0] += gap
            max0[2] += gap
        if cache is None:
            cache = []
        if not cache:
            cache[:] = Thing.objects.filter(parentid=self.parentid)
        for athing in cache:
            if athing.pk == self.pk: continue
            min1, max1 = athing.get_bounding_box()
            if not (min0[0] > max1[0] or min0[2] > max1[2] or min1[0] > max0[0] or min1[2] > max0[2]):
                 ret.append(athing)
                 if first_only:
                     break
                 
        return ret
    
    def get_api_dict(self):
        ret = super(Thing, self).get_api_dict()
        #ret['actions'] = self._generate_actions()
        ret['actions'] = self.get_actions()
        return ret
    
    @classmethod
    def get_actions(cls):
        '''Get the list of actions for this Thing. Read from disk cache, then 
        cache it in class variable.'''
        
        k = '_actions'
        ret = getattr(Thing, k, None)
        
        if ret is None:
            print 'INFO: READ actions from disk cache'
            ret = json.loads(cache.get('actions', '{}'))
            if not ret:
                ret = cls.cache_actions()
            setattr(Thing, k, ret)

        ret = ret.get(cls.module, [])
        
        return ret
        
    @classmethod
    def cache_actions(cls):
        '''Cache all the actions from all the types of things'''
        import os
        ret = {}
        
        print 'INFO: GENERATE ACTION CACHE'
        
        for afile in os.listdir(os.path.dirname(__file__)):
            if afile.endswith('.py'):
                module_key = afile.replace('.py', '')
                if module_key == '__init__': continue
                thing_class = cls.get_class_from_module_key(module_key)
                ret[module_key] = thing_class._generate_actions()
        
        cache.set('actions', json.dumps(ret))
        
        return ret

    @classmethod
    def _generate_actions(cls):
        '''Generate the list of actions supported by this type of Thing'''
        import inspect
        ret = []
        
        for method_name in dir(cls):
            method = getattr(cls, method_name)
            if inspect.ismethod(method):
                margs = inspect.getargspec(method)
                if len(margs) > 1 and margs.args[0:2] == ['self', 'actor']:
                    action = {k: 0.0 for k in margs.args[2:]}
                    action['action'] = method_name
                    ret.append(action)
        
        return ret
    
        