from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box
from unsccore.things.thing import Thing, ThingParentError
from unsccore.things.world import World
from unsccore import mogels

class Command(BaseCommand):
    help = 'Unscripted core management commands'

    def add_arguments(self, parser):
        parser.add_argument('worldid', metavar='worldid', nargs=1, type=str)
        parser.add_argument('case', metavar='case', nargs=1, type=str)

    def handle(self, *args, **options):
        found = 0
        
        worldid = options['worldid'][0]
        case = options['case'][0]
        
        world = Thing.objects.get(pk=worldid)
        found = 0
        
        if case == 'repop_fitness':
            self.repop(world, [20,1,20])
            found = 1

        if case == 'repop':
            self.repop(world)
            found = 1
            
        if not found:
            print 'ERROR: Test case not found (%s)' % case
        
        print 'done'
        
    def repop(self, world, bot_dims=None):
        world.delete_children()
        while True:
            thing = Thing.new(module='bot', parentid=world.pk)
            if bot_dims:
                thing.dims = bot_dims
            try:
                thing.save()
            except ThingParentError:
                break
        