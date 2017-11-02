from unsccore.things.thing import Thing

vision_radius = 50.0
action_radius = 1

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
            if action not in ['pass']:
                action_method = getattr(target, action, None)
                if action_method:
                    targets = actor.get_obstructing_things(cache=[target], gap=action_radius)
                    if targets:
                        action_method(actor=actor, **kwargs)
                    else:
                        print 'Not within reach'
                        pass
                else:
                    raise EngineError('Unknown action "%s"' % action)
        
            # Get all the things near actor
            # TODO: optimise!
            cache = []
            ret = actor.get_obstructing_things(cache=cache, gap=vision_radius)
            
            ret.append(Thing.objects.get(pk=actor.rootid))
        
        return ret
    
