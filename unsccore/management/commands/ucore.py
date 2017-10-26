from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box
from unsccore.things.thing import Thing
from unsccore.things.world import World
from unsccore import mogels

class Command(BaseCommand):
    help = 'Unscripted core management commands'

    def add_arguments(self, parser):
        parser.add_argument('class', metavar='class', nargs=1, type=str)
        parser.add_argument('action', metavar='action', nargs=1, type=str)
        parser.add_argument('ids', nargs='*', type=str)

    def handle(self, *args, **options):
        found = 0
        
        if 'world' in options['class']:
            worlds = []
            
            if 'add' in options['action']:
                found = 1
                if len(options['ids']) > 1:
                    worldid = options['ids'].pop(0)
                    world = World.objects.filter(pk=worldid).first()
                    if world:
                        for module_key in options['ids']:
                            print 'create %s' % module_key
                            thing = Thing.new(module=module_key)
                            world.add_thing(thing)

            if 'thing' in options['action']:
                found = 1
                if len(options['ids']) > 0:
                    worldid = options['ids'].pop(0)
                    world = World.objects.filter(pk=worldid).first()
                    c = 0
                    for box in Box.objects.filter(parent=world.box):
                        #print '#%s %s [%s] (%s, %s)' % (box.pk, box.created, box.cls.module, box.x, box.y)
                        print box.spprint()
                        c += 1
                    print '%s things found.' % c

            if 'purge' in options['action']:
                raise Exception('not yet implemented')

            if 'create' in options['action']:
                found = 1
                worlds = [World.objects.create()]
                
            if 'ls' in options['action']:
                found = 1
                worlds = World.objects.all().order_by('pk')
                print '%s worlds found.' % worlds.count()
                
            for world in worlds:
                print world.spprint()
                
            if 'rm' in options['action']:
                found = 1
                c = 0
                for world in World.objects.all():
                    if 'ALL' in options['ids'] or str(world.pk) in options['ids']:
                        print 'deleting %s %s' % (world.pk, world.created)
                        world.delete()
                        c += 1
                print '%s worlds deleted.' % c

        if not found:
            print 'ERROR: action not found'
        else:
            print 'done'
            