from Api.EndpointProperties import Property

__author__ = 'dracks'

import json


class Model(object):
    _name = None
    _fields = []
    _pk = 'id'
    _manager = None

    def __init__(self, data=None):
        if not data:
            data = {}
        self.__data = {}

        for field in self._fields:
            value = data.get(field, None)
            # print field, value
            if hasattr(self, field):
                attr = getattr(self, field)
                self.__data[field] = attr.instantiate(value)
            else:
                attr = Property(value)
                self.__data[field] = attr

    def __getattribute__(self, item):
        if item[0] == '_':
            return object.__getattribute__(self, item)
        else:
            curr = self.__data.get(item, None)
            if curr:
                return curr.get()
            else:
                return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if key[0] == '_':
            object.__setattr__(self, key, value)
        elif key in self._fields:
            curr = self.__data.get(key, None)
            if curr:
                curr.set(value)
            else:
                self.__data[key] = curr
        else:
            object.__setattr__(self, key, value)

    @classmethod
    def get(cls, request=None, query=None):
        return cls._manager.query(cls, request, query)

    @classmethod
    def get_all(cls):
        list_data = []
        reply_has_data = True
        while reply_has_data:
            data = cls.get(query="offset={0}&count=100".format(len(list_data)))
            reply_has_data = len(data) > 0
            list_data.extend(data)

        return list_data

    def get_pk(self):
        return getattr(self, self._pk)

    def raw(self, attr):
        return self.__data.get(attr, None).value

    def save(self):
        serialized = {}
        _data = self.__data
        for field in self._fields:
            v = _data.get(field, None)
            if v:
                serialized[field] = v.serialize()

        pk = self.get_pk()
        response = None
        data = json.dumps({self._name[0]: serialized})
        con = self._manager._con
        if pk:
            response = con.request_data("PUT", self._name[1] + "/" + pk, data)
        else:
            response = con.request_data("POST", self._name[1], data)

        try:
            newdata = json.loads(response.response_body)
            single = newdata.get(self._name[0], None)
            assert single, "Should return a json with an object of type single. Response:" + response.response_body
            for field in self._fields:
                attribute = _data.get(field, None)
                attribute._set(single.get(field, None))

        except ValueError, e:
            print self._name[1]
            print response.response_body
            raise e

        return self
