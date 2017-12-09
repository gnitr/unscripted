from builtins import range
from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box
from unsccore.things.thing import Thing, ThingParentError
from unsccore.things.world import World
from unsccore import mogels
from unsccore.api_client import API_Client, UnscriptedApiError
import time
from unsccore.engine import WorldEngine
from random import random
from time import sleep
import asyncio
from concurrent.futures import ThreadPoolExecutor
from unsccore.dbackends.utils import scall

class Command(BaseCommand):
    help = 'Unscripted core management commands'

    def add_arguments(self, parser):
        parser.add_argument('worldid', metavar='worldid', nargs=1, type=str)
        parser.add_argument('case', metavar='case', nargs=1, type=str)
        parser.add_argument('--cycles', nargs='?', type=int)
        parser.add_argument('--stop', action='store_true')

    def handle(self, *args, **options):
        self.api = API_Client()

        self.options = options

        worldid = options['worldid'][0]

        print('World %s' % worldid)

        case = options['case'][0]

        found = 0

        if case == 'conn':
            self.conn()
            found = 1

        if case == 'api':
            api = API_Client()
            res = api.get_things()

            print(res)

            found = 1

        if case == 'pactions':
            self.pactions(worldid)
            found = 1

        if case == 'repop_fitness':
            self.repop(worldid, [20, 1, 20])
            found = 1

        if case == 'repop':
            self.repop(worldid)
            found = 1

        if case == 'repop_well':
            self.repop_well(worldid)
            found = 1

        if case == 'simulate':
            self.simulate(worldid)
            found = 1

        if not found:
            print('ERROR: Test case not found (%s)' % case)

        print('done')

    def repop(self, worldid, bot_dims=None):
        # delete children
        print('Empty the world')

        if worldid == 'any':
            world = self.api.first(module='world')
        else:
            world = self.api.first(id=worldid)

        if world is None:
            print('ERROR: world not found')
            return

        worldid = world['id']

        for thing in self.api.find(rootid=worldid):
            if thing['id'] != worldid:
                self.api.delete(id=thing['id'])

        female = 1
        # while True:
        for i in range(10):
            try:
                self.api.create(
                    module='bot',
                    parentid=worldid,
                    female=female,
                    rootid=worldid)
            except UnscriptedApiError:
                break
            female = 1 - female

        return worldid

    def repop_well(self, worldid):
        #world.set_dims([10, 10, 10])
        # world.save()
        worldid = self.repop(worldid)

        for i in range(0, 2):
            self.api.create(module='well', parentid=worldid, rootid=worldid)

    def start_new_cycle(self, cycle):
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
                target_speed = (1.0 / walking_step_duration) * \
                    target_population * target_speed_ratio
                print('%.2fs cycles/s (%.2f x slower). %d cycles in %.2f s' % (speed, target_speed / speed, cycle_window, elapsed))

#                 world.perf = {
#                     'cycle_per_second': speed,
#                     'speed_ratio': target_speed / speed,
#                 }

                self.bins[int(speed)] = self.bins.get(int(speed), 0) + 1

            self.t0 = time.time()
            

        return cycle

    def pactions(self, worldid):

#         for t in Thing.objects.all():
#             t.delete()

        engine = WorldEngine()

        if worldid == 'any':
            world = Thing.objects.filter(module='world').first()
        elif worldid == 'new':
            world = World()
            world.save()
        else:
            world = Thing.objects.get(pk=worldid)

        abot = Thing.objects.filter(module='bot', rootid=world.pk).first()

        print(abot.pos)

        limit = self.options.get('cycles') or 10

        if abot:
            print('bot %s %s' % (abot.pk, abot.name))
            for i in range(limit):
                print(i)
                engine.action(
                    targetid=world.pk,
                    action='walk',
                    actorid=abot.pk,
                    angle=random())

    def simulate(self, worldid):
        import uvloop
        #asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.bins = {}

        if worldid == 'any':
            worldid = scall(self.api.first(module='world'))['id']
        print('World %s' % worldid)

        limit = self.options.get('cycles')

        cycle = -1

        self.bots = {}

        t0 = time.time()
        
        while True:
            cycle = self.start_new_cycle(cycle)

            if limit is not None and cycle >= limit:
                break

            print('Cycle: %s' % cycle)
            botids = sorted(
                [t['id'] for t in scall(self.api.find(module='bot', rootid=worldid))])

            if not botids:
                break

            # TODO: remove dead bots from <bots>
            self.run_cycle(botids)
            
            # world.end_cycle()
            # time.sleep(0.1)

        t1 = time.time()
        
        for speed in sorted(self.bins.keys()):
            print('%s, %s' % (speed, self.bins[speed]))

        print('%s reqs./s.' % int(limit / (t1 - t0) * 11))

        if self.options.get('stop'):
            self.api.stop()
        
    def run_cycle(self, botids):
        futures = []
        
        from unscbot.models import Bot
        for botid in botids:
            bot = self.bots.get(botid, None)
            if bot is None:
                self.bots[botid] = bot = Bot(botid, self.api)
                bot.initialise()
            futures.append(bot.select_and_call_action())
            #scall(bot.select_and_call_action())
        
        loop = asyncio.get_event_loop()
        #loop.set_default_executor(ThreadPoolExecutor(1000))
        loop.run_until_complete(asyncio.gather(*futures))

    def run_cycle_old(self, botids):
        from unscbot.models import Bot
        for botid in botids:
            bot = self.bots.get(botid, None)
            if bot is None:
                self.bots[botid] = bot = Bot(botid, self.api)
                bot.initialise()
            bot.select_and_call_action()
        
    def conn(self):
        t0 = time.time()

        cycles = self.options.get('cycles')

        o = 0
        for i in range(cycles):
            # print i
            r = self.api.send_request('', i=i)
            # sleep(0.00001)

        t1 = time.time()

        print('%s reqs./s.' % int(cycles / (t1 - t0)))
