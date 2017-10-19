# -*- coding: utf-8 -*-
# TODO: document the models

from __future__ import unicode_literals
import datetime

from django.db import models

class TimeStamped(models.Model):
    '''
    Abstract model to keep track of creation and last update date times.
    '''
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class ThingClass(TimeStamped):
    '''
    A type of Thing, e.g. a world, a bot, a tree, ...
    '''
    module = models.SlugField('Python module', unique=True, help_text='the name of the python module that contains the management class for this type of thing.')

class Box(TimeStamped):
    '''
    A box contains the physical information about a Thing:
    The position (x, y, z). Note that the coordinates are relative to the parent's coordinates.
    The bounding box (w, h, d)
    The containing box (parent)
    The type of thing (cls)
    '''
    x = models.FloatField(default=0.0, db_index=True)
    y = models.FloatField(default=0.0, db_index=True)
    z = models.FloatField(default=0.0, db_index=True)

    w = models.FloatField('width', default=0.0)
    h = models.FloatField('height', default=0.0)
    d = models.FloatField('depth', default=0.0)
    
    parent = models.ForeignKey('self', null=True, help_text='Link to the Box that contains this box. Might be null for a World.')
    
    cls = models.ForeignKey(ThingClass)
    
class Boxed(TimeStamped):
    '''
    Abstract model that simply link to a Box. Every Thing should be Boxed.
    '''
    box = models.ForeignKey(Box, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
    
class World(Boxed):
    '''
    A Virtual World that contains things (bots and non-bots).
    '''
    pass
    
class Bot(Boxed):
    '''
    A Bot
    '''
    pass
