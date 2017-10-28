from django.core.management.base import BaseCommand, CommandError
#from unsccore.models import World, Box

class Command(BaseCommand):
    help = 'Unscripted bot management commands'

    def add_arguments(self, parser):
        parser.add_argument('id', metavar='id', nargs=1, type=str)
        parser.add_argument('action', metavar='action', nargs=1, type=str)
        parser.add_argument('params', nargs='*', type=str)

    def handle(self, *args, **options):
        found = 0
        
        botid = options['id'][0]
        action = options['action']
        if 'live' in action:
            found = 1
            
            from unscbot.models import Bot
            bot = Bot(botid)
            bot.live()
            
        print 'done'
