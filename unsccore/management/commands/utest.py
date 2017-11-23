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
        parser.add_argument('--cycles', nargs='?', type=int)

    def handle(self, *args, **options):
        found = 0
        self.options = options
        
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
        world.recreate()
        female = 1
        while True:
            thing = Thing.new(module='bot', parentid=world.pk, female=female)
            if bot_dims:
                thing.dims = bot_dims
            try:
                thing.save()
            except ThingParentError:
                break
            
            female = 1 - female
    
    def repop_well(self, world):
        world.set_dims([10, 10, 10])
        self.repop(world)
        world.save()

        for i in range(0, 2):
            Thing.new(module='well', parentid=world.pk).save()
    
    def simulate(self, world):
        t0 = time.time()
        
        from unscbot.models import Bot
        
        limit = self.options.get('cycles')
        
        cycle = 0
        
        while True:
            if limit is not None and cycle >= limit:
                break
            cycle += 1
            print 'Cycle: %s' % cycle
            botids = [t.pk for t in Thing.objects.filter(module='bot', parentid=world.pk).order_by('pk')]
        
            if not botids:
                break
        
            for botid in botids:
                bot = Bot(botid)
                bot.initialise()
                bot.select_and_call_action()
            
            world.end_cycle()
            world.save()
            #time.sleep(0.1)
                
        t1 = time.time()
        
        elapsed = t1 - t0
        speed = cycle / elapsed 
        # For the server side to support 100 bots to act in real time
        walking_step_duration = 0.6
        target_population = 100
        # compress 4M years of evolution in 40000 years 
        target_speed_ratio = 100
        target_speed = (1.0 / walking_step_duration) * target_population * target_speed_ratio
        print '%.2fs cycles/s (%.2f x slower). %d cycles in %.2f s' % (speed, target_speed / speed, cycle, elapsed)
        
        