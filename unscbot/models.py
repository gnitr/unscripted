# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from random import random
import requests
import json

# Create your models here.
class Bot(object):
    
    def __init__(self, botid):
        self.botid = botid
        
    def initialise(self):
        self.interact(action='pass')
        
    def live(self):
        
        self.initialise()
        
        import time
        while True:
            self.interact(action='walk', target=self.world.id, angle=random())
            time.sleep(1)
    
    def interact(self, action, **kwargs):
        # https://stackoverflow.com/questions/17301938/making-a-request-to-a-restful-api-using-python
        import urllib
        qs = urllib.urlencode(kwargs)
        url = 'http://localhost:8000/api/1/bots/%s/action/%s?%s' % (self.botid, action, qs)
        print url
        res = requests.get(url)
        
        if res.ok:
            res_content = json.loads(res.content)
            
            if res_content['data']:
                self.items = res_content['data']['items']
                for item in self.items:
                    if item['module'] == 'world':
                        self.world = item
                    if item['id'] == self.botid:
                        self.data = item
            else:
                print 'WARNING: interaction error %s' % res_content['error']
        else:
            print 'WARNING: API request error %s' % res.status_code
        