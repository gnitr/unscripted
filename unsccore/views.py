# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .api import UnscriptedAPI
from django.views.decorators.csrf import csrf_exempt
from unsccore.dbackends import utils as dbutils
import os
import asyncio

api = UnscriptedAPI()


@csrf_exempt
def view_api(request, path):
    
    try:
        loop = asyncio.get_event_loop()
    except Exception as e:
        loop = asyncio.set_event_loop(asyncio.new_event_loop())

    res = dbutils.scall(api.process(request, path))
    
    # return JsonResponse(res, safe=False, status=api.get_status())
    return HttpResponse(dbutils.json.dumps(
        res), content_type='application/json', status=api.get_status(res))
