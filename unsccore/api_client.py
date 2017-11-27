import requests
import json

class UnscriptedApiError(Exception):
    pass 

class API_Client(object):
    
    def __init__(self):
        # TODO: set dynamically
        self.api_root = 'http://localhost:8000/api/1/'
        self.items = None
    
    def action(self, targetid, action, **kwargs):
        return self.send_request('things/%s/actions/%s' % (targetid, action), **kwargs)
    
    def delete(self, **query):
        query['@method'] = 'DELETE'
        return self.send_request('things', **query)
    
    def create(self, **query):
        query['@method'] = 'POST'
        res = self.send_request(query['module'], **query)
        return res[0]
    
    def find(self, **query):
        return self.request_things(**query)
    
    def first(self, **query):
        res = self.find(**query)
        if len(res):
            return res[0]
        return None

    def request_things(self, **query):
        return self.send_request('things', **query)
    
    def send_request(self, path, **query):
        self.items = None
        
        # https://stackoverflow.com/questions/17301938/making-a-request-to-a-restful-api-using-python
        import urllib
        qs = urllib.urlencode(query)
        url = self.api_root + path + '?' + qs
        print url
        
        res = None
        try:
            res = requests.get(url)
        except requests.exceptions.ConnectionError:
            # fails silently
            pass
        
        if res is not None:
            res_content = json.loads(res.content)
            error = res_content.get('error')
            if error:
                raise UnscriptedApiError('WARNING: processing error %s' % res_content['error']['message'])
            
            if res_content['data']:
                self.items = res_content['data']['items']
            else:
                raise UnscriptedApiError('WARNING: unknown processing error')
        else:
            raise UnscriptedApiError('WARNING: API connection error')
        
        return self.items

