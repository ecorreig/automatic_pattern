__author__ = 'dracks'

from Connector import Connector
import json

import sys, traceback

# from EndpointModel import Model as AbstractModel

class DataManager:
    __manager = None

    @classmethod
    def sharedManager(cls):
        """

        :return: DateManager
        """
        if not cls.__manager:
            cls.__manager = cls()

        return cls.__manager

    @classmethod
    def endpoint(cls, model):
        manager = cls.sharedManager()
        model._manager = manager
        manager._models_dict[model._name[0]] = model
        return model

    def __init__(self):
        self._models_dict = {}
        self._cache = {}
        self._get_connection()

    def set_config(self, config):
        self._get_connection(config)

    def _get_connection(cls, config='config.json'):
        conf = json.load(open(config, 'r'))
        cls._con = Connector(conf['host'], conf['path'], conf['token'])

    def query(self, cls, request=None, query=None):
        """

        :param cls:
        :type cls: EndpointModel.Model or str
        :param request:
        :param query:
        :return:
        """
        if isinstance(cls, str):
            cls_name=cls
            cls = self.get(cls)
            assert cls is not None, "The class name {c} is not registered".format(c=cls_name)

        call = cls._name[1]
        if request:
            call = call + "/" + request
        if query:
            call = call + "?" + query

        response = self._con.request_data("GET", call, "")
        try:
            data = json.loads(response.response_body)
            single = data.get(cls._name[0], None)
            if single is None:
                data = data.get(cls._name[1], None)
                assert (data is not None), response.response_body
                list_objects = map(cls, data)
                for obj in list_objects:
                    self.__register_cache(obj)
                return list_objects
            else:
                obj = cls(single)
                self.__register_cache(obj)
                return obj
        except ValueError, e:
            print call
            print response.response_body
            type_, value_, traceback_ = sys.exc_info()
            print "".join(traceback.format_exception(type_, value_, traceback_))
            raise e

    def __register_cache(self, obj):
        """
        Register an object to the cache
        :param obj:
        :type obj: AbstractModel
        :return:
        """
        model = obj._name[0]
        pk = obj.get_pk()
        model_cache = self._cache.get(model, None)
        if model_cache is None:
            model_cache = {}
            self._cache[model] = model_cache
        model_cache[pk] = obj

    def retrieve(self, model, id):
        model_cache = self._cache.get(model, None)
        if model_cache is None:
            model_cache = {}
            self._cache[model] = model_cache
        cache = model_cache.get(id, None)
        if cache is None:
            cache = self.query(model, id)
            model_cache[id] = cache
        return cache

    def retrieve_all(self, model):
        model_cache = self._cache.get(model, None)
        if model_cache is None:
            return []
        else:
            return map(lambda e: model_cache[e], model_cache.keys())

    def get_all(self, model):
        list_data = []
        reply_has_data = True
        while reply_has_data:
            data = self.query(model, query="offset={0}&count=100".format(len(list_data)))
            reply_has_data = len(data) > 0
            list_data.extend(data)

            return list_data

    def get(self, name):
        """
        Get a class from the models dictionary
        :param name:
        :return:
        :rtype: class or None
        """
        return self._models_dict.get(name, None)
