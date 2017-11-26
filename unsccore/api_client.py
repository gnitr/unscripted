import requests
import json

class API_Client(object):
    
    def __init__(self):
        # TODO: set dynamically
        self.api_root = 'http://localhost:8000/api/1/'
        self.items = None
    
    def action(self, targetid, action, **kwargs):
        return self.send_request('things/%s/actions/%s' % (targetid, action), **kwargs)
    
    def get_things(self, **query):
        return self.request_things(**query)
    
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
        
        if res and res.ok:
            res_content = json.loads(res.content)
            
            if res_content['data']:
                self.items = res_content['data']['items']
            else:
                print 'WARNING: interaction error %s' % res_content['error']
        else:
            if res:
                print 'WARNING: API request error %s' % res.status_code
            else:
                print 'WARNING: API connection error'
        
        return self.items

