from django.conf import settings
import pymongo
import re
import json
from datetime import datetime
from bson.objectid import ObjectId
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

def get_class_name_from_module_key(module_key):
    ''' my_class -> MyClass '''
    return re.sub(r'((^|_)[a-z])', lambda m: m.group(1).upper(), module_key.lower()).replace('_', '')

def get_key_from_class_name(class_name):
    ''' MyClass -> my_class'''
    return re.sub(r'([A-Z])', r'_\1', class_name).strip('_').lower()

# dictionary conversion among 
# Mongo DB document, Django Model __dict__ and Web API json dict
def get_mongo_dict_from_model_dict(d):
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
            v = get_mongo_dict_from_model_dict(v)
        elif isinstance(v, basestring) and len(v) == len('59ea5544274d0a2924d8b06b') and k.endswith('id'):
            v = ObjectId(v)
        ret[k] = v
    return ret

def get_model_dict_from_mongo_dict(d):
    ret = {}
    for k, v in d.iteritems():
        if k == '_id':
            k = 'pk'
        if k.startswith('_'): continue
        if isinstance(v, dict):
            v = get_model_dict_from_mongo_dict(v)
        elif isinstance(v, ObjectId):
            v = str(v)
        ret[k] = v
    return ret

def get_api_dict_from_model_dict(d):
    ret = {}
    for k, v in d.iteritems():
        if k == 'pk':
            k = 'id'
        if k.startswith('_'): continue
        if isinstance(v, dict):
            v = get_api_dict_from_model_dict(v)
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

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class MongoQuerySet(object):
    '''
    A pymongo query builder and cursor over a result 
    that implements some of the django QuerySet interface.
    '''
    # TODO: any call modifying the query should return a NEW instance
    # e.g. q = .all(); q2 = q.filter(pk=123)
    
    _client = None
    _db = None
    
    def __init__(self, doc_class):
        self.reset_query()
        self.query_executed_hash = None
        self.doc_class = doc_class
        
    def reset_query(self):
        self.query = {'filters': {}, 'order': None}
    
    def clone(self):
        import copy
        ret = MongoQuerySet(self.doc_class)
        ret.query = copy.deepcopy(self.query)
        return ret
    
    def __iter__(self):
        return self.clone()
    
    def next(self):
        cursor = self._get_cursor()
        doc = cursor.next()
        ret = self.doc_class.new(**doc)
        return ret

    @classmethod
    def _get_db(cls):
        if not cls._db:
            cls._client = pymongo.MongoClient('mongodb://%s:%s/' % (
                settings.DB_THINGS['HOST'],
                settings.DB_THINGS['PORT']
            ))
            cls._db = cls._client[settings.DB_THINGS['NAME']]
        return cls._db

    def create(self, **kwargs):
        obj = self.doc_class.new(**kwargs)
        ret = obj.save()
        return obj
    
    def all(self):
        ret = self.clone()
        return ret

    def filter(self, **filters):
        ret = self.clone()
        if filters:
            ret.query['filters'].update(filters)
        return ret
    
    def __getitem__(self, key):
        # can raise IndexError
        cursor = self._get_cursor()
        return self.doc_class.new(**cursor[key])
    
    def get(self, **filters):
        docs = self.filter(**filters)
        c = docs.count()
        if c == 0:
            raise ObjectDoesNotExist('Thing not found (%s)' % repr(filters))
        if c > 1:
            raise MultipleObjectsReturned()
        return docs[0]
        

    def order_by(self, key):
        self.query['order'] = key
        return self
    
    def first(self):
        ret = None
        cursor = self._get_cursor()
        try:
            ret = self.doc_class.new(**cursor[0])
        except IndexError, e:
            pass
        return ret
    
    def _get_collection(self):
        # TODO: cache?
        ret = self._get_db()[self.doc_class.Meta.db_table]
        return ret
    
    def _get_cursor(self, reset=False):
        query_hash = json.dumps(self.query)
        if reset or query_hash != self.query_executed_hash:
            collection = self._get_collection()
            # TODO: query
            
            filters = get_mongo_dict_from_model_dict(self.query['filters'])
            # TODO: works for simple care field=value
            # but need to convert django operators to mongo

            print 'MONGO FIND (%s)' % repr(filters)
            self.cursor = collection.find(filters)
                
            if self.query['order']:
                orders = []
                for field in [self.query['order']]:
                    if field == 'pk': field = '_id'
                    field_name = field.strip('-')
                    order = [field_name, pymongo.ASCENDING]
                    if field_name != field: order[1] = pymongo.DESCENDING
                    orders.append(order)
                self.cursor.sort(orders)
            
            self.query_executed_hash = query_hash
        return self.cursor

    def _mongo_replace_one(self, model):
        collection = self._get_collection()
        doc = model._get_mongo_dict()
        if doc.get('_id'):
            collection.replace_one({'_id': doc['_id']}, doc)
        else:
            model.pk = str(collection.insert_one(doc).inserted_id)

    def _mongo_delete_one(self, model):
        doc = model._get_mongo_dict()
        self._get_collection().delete_one({'_id': doc['_id']})

    def count(self):
        return self._get_cursor().count()

class MongoModel(object):
    '''
    A pymongo object wrapper that  
    that implements some of the django Model interface.
    
    The object instance variables that don't start with _
    are used both like django model attributes and
    mongodb field.
    
    _get_doc and _set_doc do the conversion 
    between the dajngo model and mongo document. 
    
    The primary key field is called 'pk', NOT 'id'.
    '''
    
    def __init__(self, **kwargs):
        # _id is a Mongo ObjectId(); self.pk is a django id (string)
        self.pk = None
        self._set_mongo_dict(kwargs)
    
    class Meta:
        db_table = 'my_collection'
        abstract = True
    
    @classmethod
    def new(cls, **doc):
        # dummy behaviour, subclasses can do more with doc to
        # instantiate the right type of object
        return cls(**doc)

    @classmethod
    def get_objects(cls):
        ret = MongoQuerySet(cls)
        return ret
    
    def save(self):
        self.objects._mongo_replace_one(self)

    def delete(self):
        self.objects._mongo_delete_one(self)

    def _set_mongo_dict(self, doc):
        for k, v in get_model_dict_from_mongo_dict(doc).iteritems():
            setattr(self, k, v)

    def _get_mongo_dict(self):
        return get_mongo_dict_from_model_dict(self.__dict__)
    
    def get_api_dict(self):
        return get_api_dict_from_model_dict(self.__dict__)
    
    objects = ClassProperty(get_objects)
    
class MongoDocumentModule(MongoModel):
    '''
    A MongoModel that allow to store variants of the same documents within
    the same collection. Each variant is called a module and has its own set of
    fields.
    
    self.module: determine the variant, it is also the name of the python module
    and class that will be used to instantiate the model object.
    '''
    
    def __init__(self, **kwargs):
        self.module = self.get_module_key()
        self.created = datetime.utcnow()
        super(MongoDocumentModule, self).__init__(**kwargs)
    
    @classmethod
    def new(cls, **doc):
        # TODO: error management!
        import importlib
        module_key = doc.get('module', None)
        aclass = cls.get_class_from_module_key(module_key)
        if aclass:
            ret = aclass(**doc)
        else:
            ret = super(MongoDocumentModule, cls).new(**doc)
        
        return ret
    
    @classmethod
    def get_class_from_module_key(cls, module_key):
        ret = None

        if module_key:
            import importlib
            try:
                module = importlib.import_module('.'+module_key, 'unsccore.things')
                ret = getattr(module, get_class_name_from_module_key(module_key), None)
            except ImportError:
                pass
        
        return ret
    
    @classmethod
    def get_objects(cls):
        ret = super(MongoDocumentModule, cls).get_objects()
        ret = ret.filter(module=cls.get_module_key())
        return ret

    objects = ClassProperty(get_objects)

    @classmethod
    def get_module_key(cls):
        return get_key_from_class_name(cls.__name__)
    
    def get_module_key_plural(self):
        ret = self.module
        # TODO: do other cheap pluralisations
        # anything beyond that has to be overridden by subclasses
        ret += 's'
        return ret
    
    