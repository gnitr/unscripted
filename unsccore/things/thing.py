from unsccore import mogels

class ThingParentError(Exception):
    pass

class Thing(mogels.MongoDocumentModule):
    
    class Meta:
        db_table = 'things'

    def __init__(self, **kwargs):
        # last valid parentid value
        self._parentid_valid = 1
        defaults = {
            'pos': [0.0] * 3,
            'dims': [1.0] * 3,
            'parentid': None
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
    
    def move(self):
        pass
    
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
            self.before_changing_parent()
        
#             if self.parentid:
#                 print 'h1'
#                 print self.parent._get_doc()
#                 print self.parent.__class__
#                 self.parent.add_thing(self)
#             else:
#                 if not self.can_be_root():
#                     raise ThingParentError('%s save() error. The object must have a valid parent. None specified.' % self.module)
#                 self._parentid_valid = self.parentid
        
        super(Thing, self).save()
        self._parentid_valid = self.parentid
        
    def before_changing_parent(self):
        if self.parentid:
            self.parent.before_inserting_child(self)
        if self.__class__ == Thing:
            raise ThingParentError('Generic Things cannot be added. Please add specific things.')
    
    def before_inserting_child(self, child):
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
