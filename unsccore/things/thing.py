from unsccore import mogels

class Thing(mogels.MongoDocumentModule):
    
    class Meta:
        db_table = 'things'

    def __init__(self, **kwargs):
        self.pos = [0.0] * 3
        self.dims = [1.0] * 3
        self.parentid = None
        super(Thing, self).__init__(**kwargs)
    
    def spprint(self):
        print self._get_doc()
        ret = '# %s %s <%s|%s> (%s, %s, %s)' % (
            self.pk,
            self.created,
            self.__class__.__name__, self.module,
            self.pos[0], self.pos[1], self.pos[2],
        )
        return ret
    
    def move(self):
        pass
    
