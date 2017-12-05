# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from random import random, randint
from unsccore.api_client import API_Client

# Create your models here.
class Bot(object):
    
    def __init__(self, botid, api):
        self.api = api or API_Client()
        self.botid = botid
        self.items = []
        
    def initialise(self):
        return self.interact(action='pass')
        
    def live(self):
        ret = self.initialise()
        
        if not ret:
            print('ERROR: could not connect to the API')
        else:
            import time
            while True:
                #self.interact(action='walk', target=self.world['id'], angle=random())
                self.select_and_call_action()
                time.sleep(.01)
        
        return ret

    def select_and_call_action(self):
        self.select_action()
        self.call_selected_action()
    
    def select_action(self):
        actions = [{'action': 'pass'}]
        # gather all actions into an array
        for item in self.items:
            for action in item.get('actions', []):
                action['targetid'] = item['id']
                actions.append(action)
        # select a random action from the array
        self.action = actions[randint(0, len(actions) - 1)]
        # select random values to the action arguments
        for k in self.action.keys():
            if k not in ['action', 'targetid']:
                self.action[k] = random()
        return self.action
    
    def call_selected_action(self):
        self.interact(**self.action)

    def interact(self, action, targetid=None, **kwargs):
        ret = False
        
        if targetid is None:
            targetid = self.botid
        
        # https://stackoverflow.com/questions/17301938/making-a-request-to-a-restful-api-using-python
        kwargs['actorid'] = self.botid
        
        items = self.api.action(targetid, action, **kwargs)
        
        if items:
            self.items = items
            for item in self.items:
                if item['module'] == 'world':
                    self.world = item
                if item['id'] == self.botid:
                    self.data = item
            ret = True
        
        return ret
    