from django.conf import settings
import pymongo
import re
import json
from datetime import datetime
from bson.objectid import ObjectId

def get_class_name_from_module_key(module_key):
    ''' my_class -> MyClass '''
    return re.sub(r'((^|_)[a-z])', lambda m: m.group(1).upper(), module_key.lower()).replace('_', '')

def get_key_from_class_name(class_name):
    ''' MyClass -> my_class'''
    return re.sub(r'([A-Z])', r'_\1', class_name).strip('_').lower()

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class MongoQuerySet(object):
    
    _client = None
    _db = None
    
    def __init__(self, doc_class):
        self.query = {'filters': {}, 'order': None}
        self.query_executed_hash = None
        self.doc_class = doc_class
        
    def __iter__(self):
        return self
    
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
        return self

    def filter(self, **filters):
        if filters:
            self.query['filters'].update(filters)
        return self

    def order_by(self, key):
        self.query['order'] = key
        return self
    
    def first(self):
        ret = None
        cursor = self._get_cursor()
        try:
            ret = self.doc_class(**cursor[0])
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
            
            filters = {}
            if self.query['filters']:
                for k, v in self.query['filters'].iteritems():
                    if k == 'pk': k = '_id'
                    if isinstance(v, basestring) and len(v) == len('59ea5544274d0a2924d8b06b') and k.endswith('id'):
                        v = ObjectId(v)
                    filters[k] = v
                # TODO: works for simple care field=value
                # but need to convert django operators to mongo

            print filters
            self.cursor = collection.find(filters)
                
            if self.query['order']:
                orders = []
                for field in [self.query['order']]:
                    if field == 'pk': field = '_id'
                    field_name = field.strip('-')
                    order = [field_name, pymongo.ASCENDING]
                    if field_name != field: order[1] = pymongo.DESCENDING
                    orders.append(order)
                print orders
                self.cursor.sort(orders)
            
            self.query_executed_hash = query_hash
        return self.cursor

    def count(self):
        return self._get_cursor().count()

class MongoDocument(object):
    
    def __init__(self, **kwargs):
        self._id = None
        self._set_doc(kwargs)
    
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
    
    def _set_doc(self, doc):
        for k, v in doc.iteritems():
            setattr(self, k, v)
        
    def _get_doc(self):
        ret = {}
        for k in self.__dict__:
            if k.startswith('_'):
                continue
            a = getattr(self, k)
            if not callable(a):
                ret[k] = a
        
        return ret
    
    def get_pk(self):
        return self._id

    def set_pk(self, pk):
        self._id = pk
        
    pk = property(get_pk, set_pk)
    
    def save(self):
        collection = self.objects._get_collection()
        doc = self._get_doc()
        if self.pk:
            collection.replace_one({'_id': self.pk}, doc)
        else:
            self.pk = collection.insert_one(doc).inserted_id
            
    objects = ClassProperty(get_objects)
    
class MongoDocumentModule(MongoDocument):
    
    def __init__(self, **kwargs):
        self.module = self.get_module_key()
        self.created = datetime.utcnow()
        super(MongoDocumentModule, self).__init__(**kwargs)
    
    @classmethod
    def new(cls, **doc):
        # TODO: error management!
        import importlib
        module_key = doc.get('module', None)
        if module_key:
            module = importlib.import_module('.'+module_key, 'unsccore.things')
            doc_class = getattr(module, get_class_name_from_module_key(module_key), None)
            return doc_class(**doc)
        return super(MongoDocumentModule, cls).new(**doc)
            
    
    @classmethod
    def get_module_key(cls):
        return get_key_from_class_name(cls.__name__)
    
    