from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box
from unsccore.things.thing import Thing, ThingParentError
from unsccore.things.world import World
from unsccore import mogels
import time
from unsccore.engine import WorldEngine
from random import random

class Command(BaseCommand):
    help = 'Unscripted core management commands'

    def add_arguments(self, parser):
        parser.add_argument('worldid', metavar='worldid', nargs=1, type=str)
        parser.add_argument('case', metavar='case', nargs=1, type=str)
        parser.add_argument('--cycles', nargs='?', type=int)

    def handle(self, *args, **options):
        #mogels.set_backend('mongodb')
        
        self.options = options
        
        worldid = options['worldid'][0]
        if worldid == 'any':
            world = World.objects.first()
            worldid = world.pk
        elif worldid in ['new', 'tmp']:
            world = World()
            self.repop_well(world)
            world.save()
            worldid = world.pk
        else: 
            world = Thing.objects.get(pk=worldid)
            
        print 'World %s' % world.pk
        
        case = options['case'][0]
        
        found = 0
        
        if case == 'pactions':
            self.pactions(world)
            found = 1

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
            
        if options['worldid'][0] in ['tmp']:
            print 'delete world %s' % world.pk
            world.delete()
        
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
        world.save()
        self.repop(world)
        world.save()

        for i in range(0, 2):
            Thing.new(module='well', parentid=world.pk).save()
            
    def start_new_cycle(self, cycle, world):
        cycle += 1
        cycle_window = 5
        if cycle % cycle_window == 0:
            if cycle > 0:
                self.t1 = time.time()
                
                elapsed = self.t1 - self.t0
                speed = cycle_window / elapsed 
                # For the server side to support 100 bots to act in real time
                walking_step_duration = 0.6
                target_population = 100
                # compress 4M years of evolution in 40000 years 
                target_speed_ratio = 100
                target_speed = (1.0 / walking_step_duration) * target_population * target_speed_ratio
                print '%.2fs cycles/s (%.2f x slower). %d cycles in %.2f s' % (speed, target_speed / speed, cycle_window, elapsed)
                
                world.perf = {
                    'cycle_per_second': speed,
                    'speed_ratio': target_speed / speed,
                }
                
            self.t0 = time.time()
            
        return cycle
    
    def pactions(self, world):
        engine = WorldEngine()
        
        abot = Thing.objects.filter(module='bot', rootid=world.pk).first()
        
        if abot is None:
            print 'ERROR: this world has no bot'
            return
        
        print abot.pos
        
        limit = self.options.get('cycles') or 10

        if abot:
            print 'bot %s %s' % (abot.pk, abot.name)
            for i in xrange(limit):
                print i
                engine.action(targetid=world.pk, action='walk', actorid=abot.pk, angle=random())
    
    def simulate(self, world):
        from unscbot.models import Bot
        
        limit = self.options.get('cycles')
        
        cycle = -1
        
        bots = {}
        
        while True:
            cycle = self.start_new_cycle(cycle, world)
            
            if limit is not None and cycle >= limit:
                break
            
            print 'Cycle: %s' % cycle
            botids = [t.pk for t in Thing.objects.filter(module='bot', parentid=world.pk).order_by('pk')]
        
            if not botids:
                break
        
            # TODO: remove dead bots from <bots>
            for botid in botids:
                bot = bots.get(botid, None)
                if bot is None:
                    bots[botid] = bot = Bot(botid)
                    bot.initialise()
                bot.select_and_call_action()
            
            world.end_cycle()
            world.save()
            #time.sleep(0.1)
        
        world.save()
                
        