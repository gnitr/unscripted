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
        ret.reset_query()
        return ret

    def filter(self, **filters):
        ret = self.clone()
        if filters:
            ret.query['filters'].update(filters)
        return ret

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
            print self.query
            if self.query['filters']:
                for k, v in self.query['filters'].iteritems():
                    if k == 'pk': 
                        k = '_id'
                        #if isinstance(v, basestring) and len(v) == len('59ea5544274d0a2924d8b06b') and k.endswith('id'):
                        v = ObjectId(v)
                    filters[k] = v
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

    def _mongo_replace_one(self, doc):
        collection = self._get_collection()
        #print repr(doc.pk)
        if doc.pk:
            collection.replace_one({'_id': doc._id}, doc._get_doc())
        else:
            doc._id = collection.insert_one(doc._get_doc()).inserted_id

    def _mongo_delete_one(self, doc):
        filter = {'_id': ObjectId(doc.pk)}
        self._get_collection().delete_one(filter)

    def count(self):
        return self._get_cursor().count()

class MongoDocument(object):
    
    def __init__(self, **kwargs):
        # _id is a Mongo ObjectId(); self.pk is a django id (string)
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
    
    def save(self):
        self.objects._mongo_replace_one(self)

    def delete(self):
        self.objects._mongo_delete_one(self)

    def _set_doc(self, doc):
        for k, v in doc.iteritems():
            setattr(self, k, v)

    def _get_doc(self):
        ret = {}
        for k in self.__dict__:
            if k.startswith('_') and (k not in ['_id'] or self._id is None):
                continue
            a = getattr(self, k)
            if not callable(a):
                ret[k] = a
        
        #print ret
        return ret
    
    def get_json_dict(self, idkey='pk'):
        ret = self._get_doc()
        ret[idkey] = self.pk
        if '_id' in ret: del ret['_id']
        return ret
    
    def get_pk(self):
        return str(self._id) if self._id else None
 
    def set_pk(self, pk):
        self._id = ObjectId(pk) if pk else None
         
    pk = property(get_pk, set_pk)

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
            try:
                module = importlib.import_module('.'+module_key, 'unsccore.things')
            except ImportError:
                return None
            doc_class = getattr(module, get_class_name_from_module_key(module_key), None)
            return doc_class(**doc)
        return super(MongoDocumentModule, cls).new(**doc)
            
    
    @classmethod
    def get_module_key(cls):
        return get_key_from_class_name(cls.__name__)
    
    def get_module_key_plural(self):
        ret = self.module
        # TODO: do other cheap pluralisations
        # anything beyond that has to be overridden by subclasses
        ret += 's'
        return ret
    
    