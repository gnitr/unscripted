from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
from .things.thing import Thing, ThingParentError
from django.core.exceptions import ObjectDoesNotExist
from websockets.exceptions import ConnectionClosed
from django.http.request import HttpRequest, QueryDict
from unsccore.dbackends.utils import json

API_VERSION = '1.0.0'

class WSRequest(HttpRequest):
    
    def __init__(self, message, api_root=''):
        super(WSRequest, self).__init__()
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
        import asyncio
        import websockets
        
        if hostname == '0':
            hostname = '0.0.0.0'
        
        # TODO: check path = api/1
        async def hello(socket, path):
            try: 
                while True:
                    message = await socket.recv()
                    #print(message)
                    res = self.process_socket_message(message)
                    #print(res)
                    await socket.send(json.dumps(res))
            except ConnectionClosed:
                print('Connection closed')
        
        start_server = websockets.serve(hello, hostname, port)
        
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    def get_status(self):
        ret = 200
        if 'error' in self.response:
            ret = self.response['error']['code']
        return ret

    def process_socket_message(self, message):
        # e.g. message = 'worlds/X/things?module=bot&@method=GET'
        request = WSRequest(message)
        return self.process(request, request.get_api_path())

    def process(self, request, path):
        import uuid

        self.errors = []
        self.request = request
        self.path = path
        self.method = request.GET.get('@method', request.method).upper()

        self.response = OrderedDict([
            ['version', self.get_major_version()],
            ['context', request.GET.get('context', '')],
            ['id', uuid.uuid4().hex],
            ['method', ''],
            ['params', request.GET],
            ['data', {}],
        ])

        self._process()

        if self.errors:
            del self.response['data']
            self.response['error'] = {
                'errors': self.errors
            }
            max_code = 0
            for error in self.errors:
                if max_code < error['code']:
                    max_code = error['code']
                    self.response['error']['message'] = error['message']
                    self.response['error']['code'] = max_code

        return self.response

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

    def _process(self):
        # TODO: too long, break into sub-methods
        parts = [p for p in self.path.strip('/').split('/') if p]

        self.response['method'] = ''
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
            self.response['env'] = self.res_env
        else:
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
                params = {k: v for k, v in self.request.GET.items()}
                things = engine.action(
                    targetid=parentid, action=action, **params)
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

            self.response['method'] = api_method
            self.response['data'] = data
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
