'''
A wrapper around pymongo.

Author: Geoffroy Noel
'''

from django.conf import settings
import pymongo
from django.core.exceptions import ObjectDoesNotExist
import utils as dbutils
import json

class MongoQuerySet(object):
    '''
    A pymongo query builder and cursor over a result 
    that implements some of the django QuerySet interface.
    '''
    
    _client = None
    _db = None
    
    def __init__(self, doc_class):
        '''
        doc_class: MongoModel or subclass. Used as a default to instantiate 
        a Mongo Document. 
        '''
        self.doc_class = doc_class
        # a hash of the last query executed on Mongo by this QuerySet 
        self.query_executed_hash = None
        self.reset_query()
        
    def reset_query(self):
        self.query = {'filters': {}, 'order': None}
        
    def remove_ghost_records(self):
        print self.count()
        i = 0
        for thing in self.all():
            i += 1
            print i, thing.pk, thing.created

    def create_index(self, akeys, unique=False):
        collection = self._get_collection()
        name = 'idx_%s' % akeys
        collection.create_index(akeys, unique=unique, name=name)
    
    def clone(self):
        import copy
        ret = MongoQuerySet(self.doc_class)
        ret.query = copy.deepcopy(self.query)
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
        obj.save()
        return obj
    
    def all(self):
        # TODO: reset query?
        ret = self.clone()
        return ret

    def filter(self, **filters):
        ret = self.clone()
        if filters:
            ret.query['filters'].update(filters)
        return ret
    
    def first(self):
        try:
            return self._get_next(1)
        except StopIteration:
            return None
    
    def get(self, **filters):
        docs = self.filter(**filters)
        ret = docs.first()
        if ret is None:
            raise ObjectDoesNotExist('Thing not found (%s)' % repr(filters))
        
        return ret
        
    def count(self):
        return self._get_cursor().count()

    def order_by(self, key):
        self.query['order'] = key
        return self
    
    def __iter__(self):
        return self.clone()
    
    def next(self):
        return self._get_next()
    
    def _get_next(self, limit=0):
        cursor = self._get_cursor()
        if limit:
            cursor.limit(limit)
        doc = cursor.next()
        ret = self.doc_class.new(**doc)
        return ret

    def __getitem__(self, key):
        # can raise IndexError
        cursor = self._get_cursor()
        return self.doc_class.new(**cursor[key])
    
    def _get_collection(self):
        # TODO: cache?
        ret = self._get_db()[self.doc_class.Meta.db_table]
        return ret
    
    def _get_cursor(self, reset=False):
        query_hash = json.dumps(self.query)
        if reset or query_hash != self.query_executed_hash:
            collection = self._get_collection()
            # TODO: query
            
            filters = dbutils._get_mongo_dict_from_model_dict(self.query['filters'])
            # TODO: works for simple care field=value
            # but need to convert django operators to mongo

            ## print 'MONGO FIND (%s)' % repr(filters)
            self.cursor = collection.find(filters)
            #self.cursor.batch_size(100)
                
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

