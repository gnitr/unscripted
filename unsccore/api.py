from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
from .things.thing import Thing, ThingParentError
from django.core.exceptions import ObjectDoesNotExist
from websockets.exceptions import ConnectionClosed
from django.http.request import HttpRequest, QueryDict
from unsccore.dbackends.utils import json
from unsccore.dbackends import utils as dbutils
from unsccore.dbackends.utils import pr
import asyncio 

API_VERSION = '1.0.0'

class WSRequest(HttpRequest):
    
    def __init__(self, *args, **kwargs):
        super(WSRequest, self).__init__()
        self.reset( *args, **kwargs)
        
    def reset(self, message=None, api_root=''):
        if message:
            parts = message.split('?')
            self.api_path = parts.pop(0)
            self.path = self.api_path
            self.qs = parts.pop(0) if parts else ''
            self.GET = QueryDict(self.qs)
        self.method = 'GET'
        # TODO: dynamic
        self.META = {'HTTP_HOST': '127.0.0.1'}
        
    def get_api_path(self):
        return self.api_path

    def _get_scheme(self):
        return 'ws'
        

class UnscriptedAPI(object):

    @classmethod
    def get_major_version(self):
        return API_VERSION.split('.')[0]

    def __init__(self):
        self._threadid = dbutils.get_threadid()
        self._init_env_response()

    def _init_env_response(self):
        if 0:
            from .api_doc import UNSCRIPTED_API_ENTRY_POINTS as DOC
            data_items = DOC
            for item in data_items:
                item['links'] = [{
                    'rel': 'self',
                    'href': self.get_href(item['path'])
                }]
        from .mogels import get_backend
        from django.conf import settings
        import sys
        #server = self.request.META.get('wsgi.file_wrapper', None)
        server = None
        self.res_env = {
            'backend': str(get_backend().__module__),
            'python': sys.version,
            'platform': sys.platform,
            'server': server.__module__ if server else '',
            'debug': settings.DEBUG
        }

    def listen_to_websocket(self, hostname='127.0.0.1', port=8000):
        # slightly faster than websockets implementation
        import aiohttp
        from aiohttp import web
        
        if hostname == '0':
            hostname = '0.0.0.0'
        
        async def websocket_handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            loop = request.loop
            
            request = WSRequest()
            
            async for message in ws:
                if message.type == aiohttp.WSMsgType.TEXT:
                    #pr('process')
                    try:
                        res = await self.process_socket_message(message.data, request)
                    except dbutils.UnscriptedStopRequest:
                        print('Receive STOP request')
                        loop.stop()
                        break
                    
                    #print(res)
                    #pr('respond')
                    await ws.send_str(json.dumps(res))
                    #pr('listen')
                elif message.type == aiohttp.WSMsgType.ERROR:
                    print('ws connection closed with exception %s' %
                          ws.exception())
        
            print('websocket connection closed')
        
            return ws
        
        app = web.Application()
        app.router.add_get('/', websocket_handler)
        web.run_app(app, host=hostname, port=int(port))

    def listen_to_websocket1(self, hostname='127.0.0.1', port=8000):
        import websockets
        
        if hostname == '0':
            hostname = '0.0.0.0'
            
        request = WSRequest()
        
        # TODO: check path = api/1
        async def hello(socket, path):
            try: 
                while True:
                    message = await socket.recv()
                    #print(message)
                    res = await self.process_socket_message(message, request)
                    #print(res)
                    await socket.send(json.dumps(res))
            except ConnectionClosed:
                print('Connection closed')

        start_server = websockets.serve(hello, hostname, port)
        
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def get_status(self, response):
        ret = 200
        if 'error' in response:
            ret = response['error']['code']
        return ret

    async def process_socket_message(self, message, request):
        # e.g. message = 'worlds/X/things?module=bot&@method=GET'
        #request = WSRequest(message)
        request.reset(message)
        return await self.process(request, request.get_api_path())

    async def process(self, request, path):
        import uuid
        
        if (self._threadid != dbutils.get_threadid()):
            raise Exception('Unscripted API should be run in a single thread. Try runserver --nothreading .')

        self.errors = []
        self.request = request
        self.path = path
        self.method = request.GET.get('@method', request.method).upper()

        response = OrderedDict([
            ['version', self.get_major_version()],
            ['context', request.GET.get('@context', '')],
            ['id', uuid.uuid4().hex],
            ['method', ''],
            ['params', request.GET],
            ['data', {}],
        ])

        await self._process(response)

        if self.errors:
            del response['data']
            response['error'] = {
                'errors': self.errors
            }
            max_code = 0
            for error in self.errors:
                if max_code < error['code']:
                    max_code = error['code']
                    response['error']['message'] = error['message']
                    response['error']['code'] = max_code

        return response

    def get_links_from_thing(self, thing):
        ret = []

        if thing.pk:
            ret.append({
                'rel': 'self',
                'href': self.get_href('/'.join([thing.get_module_key_plural(), thing.pk]))
            })
            ret.append({
                'rel': 'vis',
                'href': self.get_href('/vis/worlds/%s/' % thing.rootid, is_absolute=True)
            })

        return ret

    def get_json_data_from_thing(self, thing):
        ret = thing.get_api_dict()
        links = self.get_links_from_thing(thing)
        if links:
            ret['links'] = links
        if 1:
            ret['_class'] = thing.__class__.__name__
        return ret

    async def _process(self, response):
        # TODO: too long, break into sub-methods
        parts = [p for p in self.path.strip('/').split('/') if p]

        response['method'] = ''
        api_method = None
        data_items = []
        data = {}
        request_filters = {}
        for k, v in self.request.GET.items():
            if k.startswith('@'):
                continue
            if k == 'id':
                k = 'pk'
            request_filters[k] = v
            
        #print len(parts), self.method

        if len(parts) < 1:
            api_method = 'api.get'
            response['env'] = self.res_env
        else:
            if parts[0] == 'stop':
                raise dbutils.UnscriptedStopRequest('STOP')
            
            parentid = None
            if len(parts) > 2:
                parts.pop(0)
                parentid = parts.pop(0)

            resource_type = parts.pop(0)

            athing = None

            if resource_type == 'actions':
                # TODO: test len
                # TODO: change to POST only
                action = parts.pop(0)
                from .engine import WorldEngine
                engine = WorldEngine()
                api_method = 'thing.action.%s' % action
                # seems useless, but actually needed b/c GET is a list of lists
                await asyncio.sleep(0)
                things = engine.action(
                    targetid=parentid, action=action, **request_filters)
            else:
                if parts:
                    request_filters['pk'] = parts.pop(0)
                if resource_type and resource_type != 'things':
                    request_filters['module'] = self.get_singular(
                        resource_type)
                if request_filters.get('module') == 'thing':
                    del request_filters['module']
                if parentid:
                    request_filters['parentid'] = parentid

                # print request_filters

                if self.method in ['HEAD', 'GET', 'DELETE']:

                    api_method = '%s.get' % resource_type
                    things = Thing.objects.filter(**request_filters)

                    if self.method == 'DELETE':
                        api_method = '%s.delete' % resource_type
                        for thing in things:
                            thing.delete()
                        things = []

                    if self.method == 'HEAD':
                        things = []

                if self.method == 'POST':
                    api_method = '%s.post' % resource_type
                    athing = Thing.new(**request_filters)
                    try:
                        athing.save()
                    except ThingParentError as e:
                        self.errors.append({
                            'code': 403,
                            'message': str(e)
                        })

                    if athing.pk:
                        things = [athing]
                    else:
                        things = []

            data_items = [self.get_json_data_from_thing(
                thing) for thing in things]

        if api_method:
            data['total_count'] = data['count'] = 0
            data['items'] = data_items
            data['count'] = len(data['items'])
            data['total_count'] = data['count']

            response['method'] = api_method
            response['data'] = data
        else:
            self.errors.append({
                'code': 404,
                'message': 'Resource type not found: %s' % resource_type
            })

    def get_singular(self, module_plural):
        ret = module_plural
        ret = ret.rstrip('s')
        return ret

    def get_href(self, path='', is_absolute=False):
        import re
        if is_absolute:
            abspath = [path]
        else:
            abspath = [
                re.sub(r'(.*)%s.*?' % re.escape(self.path),
                       r'\1',
                       self.request.path
                       ),
                path
            ]

        return '%s://%s/%s' % (
            self.request.scheme,
            self.request.META['HTTP_HOST'],
            '/'.join(p.strip('/') for p in abspath)
        )
