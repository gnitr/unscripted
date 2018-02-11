from django.http.request import HttpRequest
import aiohttp
from django.http.response import FileResponse
try:
    basestring
except NameError:
    # python 3
    basestring = str
from bson.objectid import ObjectId
import re
import platform
import os
try:
    import ujson as json
    if 'pypy' in platform.python_implementation().lower():
        print('INFO: ujson cause seg fault on pypy')
        raise ImportError
except ImportError:
    print('WARNING: using json (not ujson)')
    import json


class UnscriptedStopRequest(Exception):
    pass

buffer = ''

# todo: move to another, more generic, utils.py
def get_django_request_from_aiohttp_request(arequest):
    request = HttpRequest()
    '''
    <CIMultiDict('Host': 'localhost:8000', 
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language': 'en-GB,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 
    'Cookie': 'csrftoken=z5nx2gwMuOLdzOG9vEoJG6MbHT73bUHK', 'DNT': '1', 
    'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 
    'Cache-Control': 'max-age=0')>
    '''
    request.META = {
        'REMOTE_ADDR': arequest.remote,
        'HTTP_HOST': arequest.headers['Host'],
        
    }
    request.content_type = arequest.content_type 
    request.GET.update(**arequest.GET)
    request.path = arequest.path
    request.method = arequest.method
    
    return request

def get_aiohttp_response_from_django_response(aresponse):
    from aiohttp import web
    '''
    def __init__(self, *, body=None, status=200,
                 reason=None, text=None, headers=None, 
                 content_type=None, charset=None):
    '''
    
    print(repr(aresponse._headers))
    
    if isinstance(aresponse, FileResponse):
        print(aresponse.streaming_content.__class__.__module__)
        ret = web.FileResponse(
            path=aresponse.streaming_content,
            headers={p[0]: p[1] for p in aresponse._headers.values()},
            status=aresponse.status_code,
        )
    else:
        ret = web.Response(
            body=aresponse.content,
            headers={p[0]: p[1] for p in aresponse._headers.values()},
            status=aresponse.status_code,
        )
    
    return ret

def pr(message):
    global buffer
    import asyncio
    taskid = str(id(asyncio.Task.current_task()))[-2:]
    tid = str(get_threadid())[-2:]
    buffer += ('%s %s %s\n' % (tid, taskid, message))
    if len(buffer) > 2000:
        print(buffer)
        buffer = ''
    #print('%s %s %s' % (tid, taskid, message))

def scall(coro):
    '''Synchronously call an async function'''
    import asyncio
    return asyncio.get_event_loop().run_until_complete(coro)
    
def get_pid():
    return os.getpid()


def is_process_active(pid):
    path = '/proc/%s' % pid
    ret = os.path.exists(path)
    return ret


def get_threadid():
    import threading
    thread = threading.currentThread()
    return thread.ident


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def get_class_name_from_module_key(module_key):
    ''' my_class -> MyClass '''
    return re.sub(r'((^|_)[a-z])', lambda m: m.group(1).upper(),
                  module_key.lower()).replace('_', '')


def get_key_from_class_name(class_name):
    ''' MyClass -> my_class'''
    return re.sub(r'([A-Z])', r'_\1', class_name).strip('_').lower()


def get_mongo_dict_from_model(model, plain_id=False):
    ret = _get_mongo_dict_from_model_dict(model.__dict__, plain_id=plain_id)
    # A bit special, .module is a class variable and therefore not part
    # of __dict__, it's thus treated slightly differently.
    ret['module'] = model.module
    return ret

# dictionary conversion among
# Mongo DB document, Django Model __dict__ and Web API json dict


def _get_mongo_dict_from_model_dict(d, plain_id=False):
    ret = {}
    for k, v in d.items():
        if callable(v):
            print('CALLABLE %s %s' % (k, v))
        if k.startswith('_'):
            continue
        if k == 'pk':
            k = '_id'
        if k == '_id' and v is None:
            continue
        if isinstance(v, dict):
            v = _get_mongo_dict_from_model_dict(v, plain_id=plain_id)
        elif not plain_id and isinstance(v, basestring) and len(v) == len('59ea5544274d0a2924d8b06b') and k.endswith('id'):
            v = ObjectId(v)
        ret[k] = v
    return ret


def get_model_dict_from_mongo_dict(d):
    ret = {}
    for k, v in d.items():
        if k == 'module':
            # .module is derived from the model class (Bot.module = 'bot')
            continue
        if k == '_id':
            k = 'pk'
        if k.startswith('_'):
            continue
        if isinstance(v, dict):
            v = get_model_dict_from_mongo_dict(v)
        elif isinstance(v, ObjectId):
            v = str(v)
        ret[k] = v
    return ret


def get_api_dict_from_model(model):
    ret = _get_api_dict_from_model_dict(model.__dict__)
    ret['module'] = model.module
    return ret


def _get_api_dict_from_model_dict(d):
    ret = {}
    for k, v in d.items():
        if k == 'pk':
            k = 'id'
        if k.startswith('_'):
            continue
        if isinstance(v, dict):
            v = _get_api_dict_from_model_dict(v)
        ret[k] = v
    return ret


def get_model_dict_from_api_dict(d):
    ret = {}
    for k, v in d.items():
        if k == 'id':
            k = 'pk'
        if k.startswith('_'):
            continue
        if isinstance(v, dict):
            v = get_model_dict_from_api_dict(v)
        ret[k] = v
    return ret
