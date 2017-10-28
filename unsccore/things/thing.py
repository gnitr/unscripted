from unsccore import mogels
from bson.objectid import ObjectId

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
            ret.reset_query()
        return ret

    objects = mogels.ClassProperty(get_objects)
    
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

    def delete(self):
        # A in B in C
        # Delete B
        # => A in C
        # TODO: deal with children and parents
        
        super(Thing, self).delete()

    def add_thing(self, thing):
        thing.parentid = self.pk
        thing.save()
