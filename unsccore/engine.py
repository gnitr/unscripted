from unsccore.things.thing import Thing

class WorldEngine(object):
    
    def action(self, actorid, action, **kwargs):
        ret = []
        
        athing = Thing.objects.get(pk=actorid)
        
        # get all the things in this world which are near thing
        ret = [
            # TODO: ! parentid is not necessarily the worldid
            athing.parent.get_api_dict()
        ]
        
        return ret
        