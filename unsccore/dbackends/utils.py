from bson.objectid import ObjectId
import re

def get_threadid():
    import threading
    thread = threading.currentThread()
    return thread.ident

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

def get_class_name_from_module_key(module_key):
    ''' my_class -> MyClass '''
    return re.sub(r'((^|_)[a-z])', lambda m: m.group(1).upper(), module_key.lower()).replace('_', '')

def get_key_from_class_name(class_name):
    ''' MyClass -> my_class'''
    return re.sub(r'([A-Z])', r'_\1', class_name).strip('_').lower()

def get_mongo_dict_from_model(model):
    ret = _get_mongo_dict_from_model_dict(model.__dict__)
    # A bit special, .module is a class variable and therefore not part 
    # of __dict__, it's thus treated slightly differently.
    ret['module'] = model.module
    return ret

# dictionary conversion among 
# Mongo DB document, Django Model __dict__ and Web API json dict
def _get_mongo_dict_from_model_dict(d):
    ret = {}
    for k, v in d.iteritems():
        if callable(v): 
            print 'CALLABLE %s %s' % (k, v)
        if k.startswith('_'): continue
        if k == 'pk':
            k = '_id'
        if k == '_id' and v is None:
            continue
        if isinstance(v, dict):
            v = _get_mongo_dict_from_model_dict(v)
        elif isinstance(v, basestring) and len(v) == len('59ea5544274d0a2924d8b06b') and k.endswith('id'):
            v = ObjectId(v)
        ret[k] = v
    return ret

def get_model_dict_from_mongo_dict(d):
    ret = {}
    for k, v in d.iteritems():
        if k == 'module':
            # .module is derived from the model class (Bot.module = 'bot')
            continue
        if k == '_id':
            k = 'pk'
        if k.startswith('_'): continue
        if isinstance(v, dict):
            v = get_model_dict_from_mongo_dict(v)
        elif isinstance(v, ObjectId):
            v = str(v)
        ret[k] = v
    return ret

def get_api_dict_from_model(model):
    ret = _get_api_dict_from_model_dict(model.__dict__)
    ret['module'] = model.module
    return ret
    
def _get_api_dict_from_model_dict(d):
    ret = {}
    for k, v in d.iteritems():
        if k == 'pk':
            k = 'id'
        if k.startswith('_'): continue
        if isinstance(v, dict):
            v = _get_api_dict_from_model_dict(v)
        ret[k] = v
    return ret

def get_model_dict_from_api_dict(d):
    ret = {}
    for k, v in d.iteritems():
        if k == 'id':
            k = 'pk'
        if k.startswith('_'): continue
        if isinstance(v, dict):
            v = get_model_dict_from_api_dict(v)
        ret[k] = v
    return ret

