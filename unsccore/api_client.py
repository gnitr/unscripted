import requests
from unsccore.dbackends.utils import json
# http://www.angryobjects.com/2011/10/15/http-with-python-pycurl-by-example/
import time
import pycurl
# TODO: Works with PyPy but is it more efficient than StringIO?
try:
    from cStringIO import StringIO as StringIO
except ImportError:
    # pypy
    from io import BytesIO as StringIO
try:
    from urllib import urlencode
except:
    # python 3
    from urllib.parse import urlencode
from unsccore.dbackends.utils import scall, pr
import aiohttp
import async_timeout

class WSSession(object):
    
    def __init__(self, api_root):
        self.socket = None
        self.api_root = api_root
        
    def get_headers(self):
        return 'NOHEADERS'
    
    async def get(self, url):
        #print(url)
        import websockets
        
        if self.socket is None:
            self.socket = await websockets.connect(self.api_root.rstrip('/'))
            
        api_path = url[len(self.api_root):]
        
        #print('select-and-call2.1 %s %s' % (url, time.time()))
        await self.socket.send(api_path)
        #print('select-and-call2.2 %s %s' % (url, time.time()))
        ret = await self.socket.recv()
        #print('select-and-call2.3 %s %s' % (url, time.time()))
            
        return ret


class Urllib3Session(object):

    def __init__(self):
        self.session = None
        
    def get_headers(self):
        return 'NOHEADERS'

    async def get(self, url):
        from urllib.parse import urlparse
        parts = urlparse(url)
        
        if self.session is None:
            from urllib3 import HTTPConnectionPool
            self.session = HTTPConnectionPool(host=parts.hostname, port=parts.port, maxsize=1)
        
        response = self.session.request('GET', parts.path + '?' + parts.query)
        ret = response.data
        
        return ret

class PyCurlSession(object):

    def __init__(self):
        c = self.c = pycurl.Curl()
        c.setopt(c.CONNECTTIMEOUT, 20)
        c.setopt(c.TIMEOUT, 20)
        #c.setopt(c.COOKIEFILE, '')
        #c.setopt(c.URL, 'http://myappserver.com/ses1')
        c.setopt(c.FAILONERROR, True)
        c.setopt(c.HTTPHEADER, ['Accept: text/html',
                                'Accept-Charset: UTF-8',
                                'Connection: keep-alive'])
        self.res = ''

    def get_headers(self):
        return self.headers

    async def get(self, url):
        self.res = None
        buf = StringIO()
        headers = StringIO()
        self.c.setopt(self.c.WRITEFUNCTION, buf.write)
        self.c.setopt(self.c.HEADERFUNCTION, headers.write)
        self.c.setopt(self.c.URL, url)
        try:
            self.c.perform()
        except pycurl.error as error:
            #errno, errstr = error
            raise error

        self.res = buf.getvalue()
        buf.close()
        self.headers = headers.getvalue()
        headers.close()
        
        return self.res

class AiohttpSession(object):

    def __init__(self):
        self.session = None

    def get_headers(self):
        return 'NOHEADERS'

    async def get(self, url):
        if not self.session:
            self.session = aiohttp.ClientSession()
            pass
            
        async with async_timeout.timeout(10):
            if 1: 
                async with self.session.get(url) as response:
                    #print('task %s response: %s' % (id(asyncio.Task.current_task()), id(response)))
                    return await response.text()
            else:
                async with await aiohttp.request('GET', url) as response:
                    ret = await response.text()
                return ret
                
        

class UnscriptedApiError(Exception):
    pass


class API_Client(object):

    def __init__(self, api_root=None):
        '''api_root: e.g. http://localhost:8000/api/1/'''
        self.request_idx = 0
        
        if api_root is None:
            from django.conf import settings
            api_root = settings.UNSCRIPTED_REMOTE_API
    
        self.api_root = api_root
        
        if self.api_root.startswith('ws'): 
            self.session = WSSession(self.api_root)
        else:
            # PyCurl is faster than requests
            #self.session = PyCurlSession()
            self.session = AiohttpSession()
            #self.session = Urllib3Session()
            #self.session = requests.Session()
        
    async def action(self, targetid, action, **kwargs):
        return await self.send_request('things/%s/actions/%s' %
                                 (targetid, action), **kwargs)

    async def delete(self, **query):
        query['@method'] = 'DELETE'
        return await self.send_request('things', **query)

    async def create(self, **query):
        query['@method'] = 'POST'
        res = await self.send_request(query['module'], **query)
        return res[0]

    def stop(self):
        return scall(self.send_request('stop'))
    
    async def find(self, **query):
        return await self.request_things(**query)

    async def first(self, **query):
        res = await self.find(**query)
        if len(res):
            return res[0]
        return None

    async def request_things(self, **query):
        return await self.send_request('things', **query)
    
    async def send_request(self, path, **query):
        ret = None
        self.request_idx += 1
        # https://stackoverflow.com/questions/17301938/making-a-request-to-a-restful-api-using-python
        context = query.get('@context')
        if context is None:
            context = str(id(self)) + '.' + str(self.request_idx)
            query['@context'] = context
        qs = urlencode(query)
        url = self.api_root + path + '?' + qs

        res = None
        try:
            res = await self.session.get(url)
        except requests.exceptions.ConnectionError as e:
            # fails silently
            raise e

        if res is not None:
            # print res.headers
            # print self.session.get_headers()
            if hasattr(res, 'content'):
                # for requests
                res_content = json.loads(res.content)
            else:
                # for pycurl
                res_content = json.loads(res)
            
            if res_content['context'] != context:
                pr('ERROR: Received wrong response. received %s, expected %s' % (res_content['context'][-3:], context[-3:]))
                exit()
                #raise Exception('Received wrong response. received %s, expected %s' % (res_content['context'], context))
            
            error = res_content.get('error')
            if error:
                raise UnscriptedApiError(
                    'WARNING: processing error %s' %
                    res_content['error']['message'])

            if res_content['data']:
                ret = res_content['data']['items']
            else:
                raise UnscriptedApiError('WARNING: unknown processing error')
        else:
            raise UnscriptedApiError('WARNING: API connection error')

        return ret
