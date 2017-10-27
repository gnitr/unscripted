'''
Created on 26 Oct 2017

'''
from django.utils.safestring import mark_safe
from django import template

register = template.Library()

@register.filter
def json(value):
    from bson import json_util
    import json
    return mark_safe(json.dumps(value, default=json_util.default))

