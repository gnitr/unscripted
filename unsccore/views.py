# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .api import UnscriptedAPI
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def view_api(request, path):
    
    api = UnscriptedAPI()
    res = api.process(request, path)
    
    return JsonResponse(res, safe=False, status=api.get_status())

