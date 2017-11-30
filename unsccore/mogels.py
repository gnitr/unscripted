from future.utils import with_metaclass
import time
from .dbackends import utils as dbutils
from django.conf import settings

QUERYSET = None


def set_backend(module_name):
    global QUERYSET
    import importlib
    module = importlib.import_module('.' + module_name, 'unsccore.dbackends')
    QUERYSET = module.MongoQuerySet
    print('UNSCRIPTED BACKEND = %s' % str(QUERYSET.__module__))


def get_backend():
    return QUERYSET


set_backend(settings.UNSCRIPTED_ENGINE_BACKEND)


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
        return QUERYSET(cls)

    def save(self):
        self.objects._mongo_replace_one(self)

    def delete(self):
        self.objects._mongo_delete_one(self)

    def _set_mongo_dict(self, doc):
        for k, v in dbutils.get_model_dict_from_mongo_dict(doc).items():
            setattr(self, k, v)

    def _get_mongo_dict(self):
        return dbutils.get_mongo_dict_from_model(self)

    def get_api_dict(self):
        return dbutils.get_api_dict_from_model(self)

    objects = dbutils.ClassProperty(get_objects)


class MongoDocumentModuleMeta(type):
    '''Used as a cache for optimisation purpose'''

    def __init__(cls, name, bases, dct):
        super(MongoDocumentModuleMeta, cls).__init__(name, bases, dct)
        cls.module = dbutils.get_key_from_class_name(cls.__name__)


class MongoDocumentModule(with_metaclass(MongoDocumentModuleMeta, MongoModel)):
    '''
    A MongoModel that allow to store variants of the same documents within
    the same collection. Each variant is called a module and has its own set of
    fields.

    self.module: determine the variant, it is also the name of the python module
    and class that will be used to instantiate the model object.
    '''

    #__metaclass__ = MongoDocumentModuleMeta

    # e.g. {'bot': <Bot>, ...}
    _ccache = {'modules_class': {}}

    def __init__(self, **kwargs):
        self.created = time.time()
        super(MongoDocumentModule, self).__init__(**kwargs)

    @classmethod
    def new(cls, **doc):
        # TODO: error management!
        module_key = doc.get('module', None)
        aclass = cls.get_class_from_module_key(module_key)
        if aclass:
            ret = aclass(**doc)
        else:
            ret = super(MongoDocumentModule, cls).new(**doc)

        return ret

    @classmethod
    def get_class_from_module_key(cls, module_key):
        ret = cls._ccache['modules_class'].get(module_key, None)

        if not ret and module_key:
            import importlib
            try:
                module = importlib.import_module(
                    '.' + module_key, 'unsccore.things')
                ret = getattr(
                    module,
                    dbutils.get_class_name_from_module_key(module_key),
                    None)
                cls._ccache['modules_class'][module_key] = ret
            except ImportError:
                pass

        return ret

    @classmethod
    def get_objects(cls):
        ret = super(MongoDocumentModule, cls).get_objects()
        ret = ret.filter(module=cls.module)
        return ret

    objects = dbutils.ClassProperty(get_objects)

#     @classmethod
#     def get_module_key(cls):
#         return cls.module

    def get_module_key_plural(self):
        ret = self.module
        # TODO: do other cheap pluralisations
        # anything beyond that has to be overridden by subclasses
        ret += 's'
        return ret
