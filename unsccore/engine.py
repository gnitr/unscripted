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
        
        # Get all the things near actor
        # TODO: optimise!
        ret = actor.get_obstructing_things(cache=None, first_only=False, gap=1.0)
        ret.append(Thing.objects.get(pk=actor.rootid))
        ret = [
            thing.get_api_dict()
            for thing in ret
        ] 
        
        return ret
    
