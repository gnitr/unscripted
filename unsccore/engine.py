from unsccore.things.thing import Thing

class EngineError(Exception):
    pass

class WorldEngine(object):
    
    def action(self, targetid, action, **kwargs):
        ret = []
        
        target = Thing.objects.get(pk=targetid)
        actor = target
        actorid = kwargs.get('actorid', None)
        if actorid:
            del kwargs['actorid']
            actor = Thing.objects.get(pk=actorid)
        
        if target:
            action_method = getattr(target, action, None)
            if action_method:
                action_method(actor=actor, **kwargs)
            else:
                raise EngineError('Unknown action "%s"' % action)
        
            # Get all the things near actor
            # TODO: optimise!
            cache = []
            vision_radius = 50.0
            ret = actor.get_obstructing_things(cache=cache, first_only=False, gap=vision_radius)
            
            ret.append(Thing.objects.get(pk=actor.rootid))
        
        return ret
    
