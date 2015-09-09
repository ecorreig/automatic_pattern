__author__ = 'dracks'

from Connector import Connector
import json


class DataManager:
    _con = None
    _models_dict = {}

    @classmethod
    def _get_connection(cls):
        conf = json.load(open('config.json', 'r'))
        cls._con = Connector(conf['host'], conf['path'], conf['token'])

    @classmethod
    def endpoint(cls, model):
        if cls._con is None:
            cls._get_connection()
        model._con = cls._con
        cls._models_dict[model._name[0]] = model
        return model

    @classmethod
    def get(cls,name):
        return cls._models_dict.get(name, None)