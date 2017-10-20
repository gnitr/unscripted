class Thing(object):
    
    @classmethod
    def new(cls, module):
        # TODO: error management!
        ret = None
        import importlib
        import inspect
        mod = importlib.import_module('.'+module.lower(), 'unsccore.things')
        print dir(mod)
        for m in dir(mod):
            m = getattr(mod, m)
            if inspect.isclass(m) and m.__name__.lower() == module.lower():
                ret = mod
                break
        return ret
    
    def move(self):
        pass