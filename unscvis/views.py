# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse

from django.shortcuts import render
from unsccore.things.world import World

# Create your views here.
def view_worlds(request, worldid):
    context = {}
    context['page_title'] = 'World'
    world = World.objects.get(pk=worldid)
    context['world'] = world
    return render(request, 'unscvis/world.html', context)
