from unsccore.things.thing import Thing

class EngineError(Exception):
    pass

class WorldEngine(object):
    
    def action(self, actorid, action, **kwargs):
        ret = []
        
        actor = Thing.objects.get(pk=actorid)
        
        targetid = kwargs.get('target', None)
        if targetid:
            del kwargs['target']
            target = Thing.objects.get(pk=targetid)
            action_method = getattr(target, action, None)
            if action_method:
                action_method(actor=actor, **kwargs)
            else:
                raise EngineError('Unknown action "%s"' % action)
        
        # get all the things in this world which are near thing
        # TODO: only return things near actor
        ret = [thing.get_api_dict() for thing in Thing.objects.filter(rootid=actor.rootid)]
        
        return ret
    
