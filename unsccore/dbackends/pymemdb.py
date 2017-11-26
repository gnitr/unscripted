'''
A simple & native python in-memory object collection.
Collections can be saved to and loaded from disk.
Single thread, single process.

Author: Geoffroy Noel
'''

from bson.objectid import ObjectId
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from bson.json_util import dumps, loads
import utils as dbutils
import json
from psutil import NoSuchProcess

class CollectionInsertedResponse(object):
    
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

import atexit

def get_collection_size_info(docs, serialised):
    return '%s things, %.4f MB' % (len(docs), len(serialised) / 1024.0 / 1024)

class Collection(object):
    
    _collections = {}
    
    @classmethod
    def get_collection(cls, key):
        ret = cls._collections.get(key)
        if ret is None:
            ret = cls._collections[key] = Collection(key)
        return ret
    
    def __init__(self, key):
        # TODO: use dynamic name for collection
        self.key = key
        if not self.lock():
            raise Exception(self.lock_error)
        self.load()
        
        atexit.register(lambda: self.save())
    
    def lock(self):
        '''Returns False if another running thread is using this collection.
        Only one thread/process can change the collection at any time.
        If returns True this process/thread will lock the collection.
        '''
        ret = True
        import os
        pid = os.getpid()
        tid = dbutils.get_threadid()
        cid = id(self)
        ptcid = '%s:%s:%s' % (pid, tid, cid)
        ptcid_last = cache.get(self.key + '.ptid', '123:1:1')
        if ptcid_last != ptcid:
            ret = False
            # last owner different from us, check if process still alive
            ptcid_last = ptcid_last.split(':')
            import psutil
            try:
                proc = psutil.Process(int(ptcid_last[0]))
                if proc.status() in [psutil.STATUS_DEAD, psutil.STATUS_ZOMBIE]: 
                    ret = True
            except NoSuchProcess:
                ret = True
        if ret:
            cache.set(self.key + '.ptid', ptcid)
            
        self.lock_error = 'Another process/thread is already using the collection (us: %s; them: %s)' % (ptcid, ptcid_last)
            
        return ret 

    def save(self):
        content = dumps(self._id_docs)
        cache.set(self.key, content)
        print 'COLLECTION WRITTEN (%s)' % (get_collection_size_info(self._id_docs, content))
        
    def load(self):
        content = cache.get(self.key) or '{}'
        self._id_docs = loads(content)
        print 'COLLECTION READ (%s)' % (get_collection_size_info(self._id_docs, content))
    
    def find(self, query):
        ret = []
        
        for doc in self._id_docs.values():
            
            match = 1
            for k, v in query.iteritems():
                if doc.get(k, None) != v:
                    match = 0
                    break
            
            if match:
                ret.append(doc)
        
        return Cursor(ret)
    
    def insert_one(self, doc):
        # TODO: check for duplicates
        doc['_id'] = doc.get('_id', None) or ObjectId()
        self._id_docs[str(doc['_id'])] = doc
        ret = CollectionInsertedResponse(doc['_id'])
        return ret

    def replace_one(self, query, doc):
        for adoc in self.find(query):
            adoc.update(doc)

    def delete_one(self, query):
        for adoc in self.find(query):
            del self._id_docs[str(adoc.get('_id'))]

class Cursor(object):
    
    def __init__(self, results):
        self.limit()
        self.results = results
        self.pos = -1
    
    def count(self):
        ret = len(self.results)
        if self._limit and self._limit < ret:
            ret = self._limit
        return ret
    
    def next(self):
        self.pos += 1
        if self.pos >= self.count():
            raise StopIteration
        return self.results[self.pos]
    
    def sort(self, orders):
        raise Exception('Sort not yet supported')

    def limit(self, limit=0):
        self._limit = limit

    def __iter__(self):
        return self

    def __item__(self, idx):
        return self.results[idx]

class MongoQuerySet(object):
    '''
    A pymongo query builder and cursor over a result 
    that implements some of the django QuerySet interface.
    '''
    
    def __init__(self, doc_class):
        '''
        doc_class: MongoModel or subclass. Used as a default to instantiate 
        a Mongo Document. 
        '''
        self._collection = Collection.get_collection('things')
        self.doc_class = doc_class
        # a hash of the last query executed on Mongo by this QuerySet 
        self.query_executed_hash = None
        self.reset_query()
        
    def reset_query(self):
        self.query = {'filters': {}, 'order': None}
        
    def create_index(self, akeys, unique=False):
        pass
    
    def clone(self):
        import copy
        ret = MongoQuerySet(self.doc_class)
        ret.query = copy.deepcopy(self.query)
        return ret
    
    def save(self):
        pass
        
    def load(self):
        pass
    
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
        return self._collection

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
                    order = [field_name, 1]
                    if field_name != field: order[1] = -1
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
