__author__ = 'dracks'

from Connector import Connector
import json


class DataManager:
    __manager = None

    @classmethod
    def sharedManager(cls):
        if not cls.__manager:
            cls.__manager=cls()

        return cls.__manager

    @classmethod
    def endpoint(cls, model):
        manager = cls.sharedManager()
        model._manager=manager
        manager._models_dict[model._name[0]] = model
        return model

    def __init__(self):
        self._models_dict={}
        self._cache={}
        self._get_connection()

    def _get_connection(cls):
        conf = json.load(open('config.json', 'r'))
        cls._con = Connector(conf['host'], conf['path'], conf['token'])

    def query(self, cls, request=None, query=None):
        if isinstance(cls, str):
            cls = self.get(cls)

        call = cls._name[1]
        if request:
            call = call +"/"+request
        if query:
            call = call + "?" + query

        response = self._con.request_data("GET", call, "")
        try:
            data = json.loads(response.response_body)
            single = data.get(cls._name[0], None)
            if single is None:
                data = data.get(cls._name[1], None)
                assert (data is not None), response.response_body
                return map(cls, data)
            else:
                return cls(single)
        except ValueError, e:
            print call
            print response.response_body
            raise e

    def get_all(self, model):
        list_data = []
        reply_has_data = True
        while reply_has_data:
            data = self.get(model, query="offset={0}&count=100".format(len(list_data)))
            reply_has_data = len(data) > 0
            list_data.extend(data)

            return list_data


    def get(cls,name):
        return cls.__manager._models_dict.get(name, None)