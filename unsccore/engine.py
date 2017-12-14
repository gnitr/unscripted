from unsccore.things.thing import Thing
from unsccore.dbackends.utils import pr

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
        world = None
        
        if actorid:
            del kwargs['actorid']
            actor = Thing.objects.get(pk=actorid)
            world = Thing.objects.get(pk=actor.rootid)
            
        if target:
            if action not in ['pass']:
                action_method = getattr(target, action, None)
                if action_method:
                    targets = actor.get_obstructing_things(cache=[target], gap=action_radius)
                    if targets:
                        action_method(actor=actor, **kwargs)
                    else:
                        pr('Not within reach')
                        pass
                else:
                    raise EngineError('Unknown action "%s"' % action)
        
            # Get all the things near actor
            # TODO: optimise!
            ret = [world, actor]
            ret.extend(actor.get_obstructing_things(cache=[], gap=vision_radius))

        alive = actor.after_action()
        
        # TODO: who should decide to create a new bot for a dead one?
        # World? engine?
        if not alive:
            actor = Thing.new(module='bot', parentid=world.pk, female=actor.female)
        
        actor.save()
            
        return ret
    
