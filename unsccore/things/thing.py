from unsccore import mogels

class Thing(mogels.MongoDocumentModule):
    
    class Meta:
        db_table = 'things'

    def __init__(self, **kwargs):
        defaults = {
            'pos': [0.0] * 3,
            'dims': [1.0] * 3,
            'parentid': None
        }
        defaults.update(kwargs)
        super(Thing, self).__init__(**defaults)
    
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
    
    def delete(self):
        # A in B in C
        # Delete B
        # => A in C
        # TODO: deal with children and parents
        
        super(Thing, self).delete()
