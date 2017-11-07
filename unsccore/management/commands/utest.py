from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box
from unsccore.things.thing import Thing, ThingParentError
from unsccore.things.world import World
from unsccore import mogels
import time

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

        if case == 'repop_well':
            self.repop_well(world)
            found = 1
            
        if case == 'simulate':
            self.simulate(world)
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
    
    def repop_well(self, world):
        self.repop(world)

        for i in range(0, 2):
            Thing.new(module='well', parentid=world.pk).save()
    
    def simulate(self, world):
        from unscbot.models import Bot
        
        cycle = 0
        
        while True:
            cycle += 1
            print 'Cycle: %s' % cycle
            botids = [t.pk for t in Thing.objects.filter(module='bot', parentid=world.pk).order_by('pk')]
        
            if not botids:
                break
        
            for botid in botids:
                bot = Bot(botid)
                bot.initialise()
                bot.select_and_call_action()
            time.sleep(0.1)
                
        
        