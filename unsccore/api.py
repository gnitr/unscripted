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
        self.method = request.GET.get('@method', request.method).upper()
        
        from mogels import get_backend
        
        self.response = OrderedDict([
            ['version', self.get_major_version()],
            ['context', request.GET.get('context', '')],
            ['id', uuid.uuid4().hex],
            ['method', ''],
            ['backend', str(get_backend().__module__)],
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
        for k, v in self.request.GET.iteritems():
            if k.startswith('@'): continue
            if k == 'id': k = 'pk'
            request_filters[k] = v
        
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
            
            athing = None
            
            if resource_type == 'actions':
                # TODO: test len
                # TODO: change to POST only
                action = parts.pop(0)
                from .engine import WorldEngine
                engine = WorldEngine()
                api_method = 'thing.action.%s' % action
                # seems useless, but actually needed b/c GET is a list of lists
                params = {k:v for k, v in self.request.GET.iteritems()}
                things = engine.action(targetid=parentid, action=action, **params)
            else:
                if parts:
                    request_filters['pk'] = parts.pop(0)
                if resource_type and resource_type != 'things':
                    request_filters['module'] = self.get_singular(resource_type)
                if request_filters.get('module') == 'thing':
                    del request_filters['module']
                if parentid:
                    request_filters['parentid'] = parentid

                #print request_filters

                if self.method in ['GET', 'DELETE']:
                    
                    api_method = '%s.get' % resource_type
                    things = Thing.objects.filter(**request_filters)

                    if self.method == 'DELETE':
                        api_method = '%s.delete' % resource_type
                        for thing in things:
                            thing.delete()
                        things = []
                        
                if self.method == 'POST':
                    api_method = '%s.post' % resource_type
                    athing = Thing.new(**request_filters)
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

            if 0:
                module = self.get_singular(resource_type)
                fields = {'parentid': parentid}
                if module != 'things':
                    fields['module'] = module
                fields.update(request_filters)
                athing = Thing.new(**fields)
                
                if athing:
                    thingid = parts.pop(0) if parts else None
                    things = athing.__class__.objects.filter(**request_filters)
                    if parentid:
                        things = things.filter(parentid=parentid)
                        
                    if thingid:
                        api_method = '%s.get' % resource_type
                        try:
                            things = [things.get(pk=thingid)]
                        except ObjectDoesNotExist:
                            # IMPORTANT: without this, /things/ID/?@method=DELETE  
                            # would delete all things if ID doesn't exists (i.e. except).
                            things = []
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
            
            data_items = [self.get_json_data_from_thing(thing) for thing in things]
                
        
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
