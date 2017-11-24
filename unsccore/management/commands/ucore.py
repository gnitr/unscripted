from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box
from unsccore.things.thing import Thing, ThingParentError
from unsccore.things.world import World
from unsccore import mogels
import time

class Command(BaseCommand):
    help = 'Unscripted core management commands'

    def add_arguments(self, parser):
        parser.add_argument('action', metavar='action', nargs=1, type=str)

    def handle(self, *args, **options):
        found = 0
        self.options = options
        
        action = options['action'][0]
        
        found = 0
        
        if action == 'compile':
            self.compile()
            found = 1

        if not found:
            print 'ERROR: action not found (%s)' % action
        
        print 'done'
        
    def compile(self):
        ret = Thing.cache_actions()
        print ret
        
        world = Thing.new(module='world')
        print world._generate_actions()
        print world.get_actions()
        
    
