from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict
from .things.thing import Thing, ThingParentError
from django.core.exceptions import ObjectDoesNotExist

API_VERSION = '1.0.0'

class UnscriptedAPI(object):
    
    @classmethod
    def get_major_version(self):
        return API_VERSION.split('.')[0]
    
    def get_status(self):
        ret = 200
        if 'error' in self.response:
            ret = self.response['error']['code']
        return ret
    
    def process(self, request, path):
        import uuid
        
        self.errors = []
        self.request = request
        self.path = path
        self.method = request.GET.get('method', request.method).upper()
        
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

    def get_link_from_thing(self, thing, rel='self'):
        ret = {}
        if thing.pk:
            ret = {
                'rel': rel,
                'href': self.get_href('/'.join([thing.get_module_key_plural(), thing.pk]))
            }
        return ret
    
    def get_json_data_from_thing(self, thing):
        ret = thing.get_api_dict()
        link = self.get_link_from_thing(thing)
        if link:
            ret['link'] = [link]
        if 1:
            ret['_class'] = thing.__class__.__name__
        if 0 and thing.parentid:
            ret['link'] = [self.get_link_from_thing(thing.parent), 'parent']
        return ret

    def _process(self):
        # TODO: too long, break into sub-methods
        parts = [p for p in self.path.strip('/').split('/') if p]
        
        self.response['method'] = ''
        api_method = None
        data = {}
        
        if len(parts) < 1:
            api_method = 'api.get'
            from .api_doc import UNSCRIPTED_API_ENTRY_POINTS as DOC
            data = {
                'items': DOC
            }
            for item in data['items']:
                item['links'] = [{
                    'rel': 'self',
                    'href': self.get_href(item['path'])
                }]
        else:
            parentid = None
            if len(parts) > 2:
                parts.pop(0)
                parentid = parts.pop(0)

            resource_type = parts.pop(0)
            module = self.get_singular(resource_type)
            athing = Thing.new(module=module, parentid=parentid)
            
            if athing:
                thingid = parts.pop(0) if parts else None
                things = athing.__class__.objects.all()
                if parentid:
                    things = things.filter(parentid=parentid)
                    
                if thingid:
                    api_method = '%s.get' % resource_type
                    #things = things.filter(pk=thingid)
                    try:
                        things = [things.get(pk=thingid)]
                    except ObjectDoesNotExist:
                        self.errors.append({
                            'code': 404,
                            'message': 'Resource not found: %s.id = %s' % (module, thingid)
                        })
                else:
                    api_method = '%s.get' % resource_type

                    if self.method == 'POST':
                        api_method = '%s.post' % resource_type
                        try:
                            athing.save()
                        except ThingParentError, e:
                            self.errors.append({
                                'code': 403,
                                'message': str(e)
                            })
                            
                        if athing.pk:
                            things = [athing]
                        else:
                            things = []

                if self.method == 'DELETE':
                    api_method = '%s.delete' % resource_type
                    for thing in things:
                        thing.delete()
                    things = []
                    
                # TODO: if ask for one return Thing in the data, not as a list
                #data['count'] = things.count()
                data['total_count'] = data['count'] = 0
                data['items'] = [self.get_json_data_from_thing(thing) for thing in things]
                data['count'] = len(data['items'])
                data['total_count'] = data['count']
                
        
        if api_method:
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

    def get_href(self, path=''):
        import re
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
