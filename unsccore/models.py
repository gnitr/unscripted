# -*- coding: utf-8 -*-
# TODO: document the models

from __future__ import unicode_literals
import datetime

from django.db import models
from django.utils.text import slugify
from random import random

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

    w = models.FloatField('width', default=100.0)
    h = models.FloatField('height', default=100.0)
    d = models.FloatField('depth', default=100.0)
    
    parent = models.ForeignKey('self', null=True, help_text='Link to the Box that contains this box. Might be null for a World.')
    
    cls = models.ForeignKey(ThingClass)

    def save(self, *args, **kwargs):
        if not self.cls_id:
            (self.cls, created) = ThingClass.objects.get_or_create(module=slugify(self.__class__.__name__))
        return super(Box, self).save(*args, **kwargs)
    
class Boxed(TimeStamped):
    '''
    Abstract model that simply link to a Box. Every Thing should be Boxed.
    '''
    box = models.ForeignKey(Box, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        box = Box()
        box.save()
        self.box = box
        print self.box.id
        return super(Boxed, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # TODO: world deletion will leave Bot records around
        for box in Box.objects.filter(parent=self.box):
            box.parent = self.parent
            if box.parent is None:
                # TODO: 2+ level of nesting will remain in DB!
                box.delete()
        self.box.delete()
        return super(Boxed, self).delete(*args, **kwargs)

class World(Boxed):
    '''
    A Virtual World that contains things (bots and non-bots).
    '''

    def add(self, module):
        from .things.thing import Thing
        thing = Thing.new(module)
        box = Box()
        box.x = random() * self.box.w
        box.y = random() * self.box.h
        box.z = random() * self.box.d
        box.w = 0.5
        box.h = 0.7
        box.d = 0.3
        (box.cls, created) = ThingClass.objects.get_or_create(module=slugify(module))
        box.parent = self.box
        box.save()
    
