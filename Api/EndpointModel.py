from Api.EndpointProperties import Property

__author__ = 'dracks'

import json


class Model:
    _name = None
    _fields = []
    _pk = 'id'
    _con = None

    def __init__(self, data=None):
        if not data:
            data = {}

        for field in self._fields:
            if hasattr(self, field):
                attr = getattr(self, field)
                setattr(self, field, attr.instantiate(data.get(field, None)))
            else:
                attr = Property(data.get(field, None))
                setattr(self, field, attr)

    @classmethod
    def get(cls, request=None, query=None):
        call = cls._name[1]
        if request is not None:
            call = call + "/" + request
        response = cls._con.request_data("GET", call, "")
        try:
            data = json.loads(response.response_body)
            single = data.get(cls._name[0], None)
            if single is None:
                data = data.get(cls._name[1], None)
                assert (data is not None)
                return map(cls, data)
            else:
                return cls(single)
        except ValueError, e:
            print call
            print response.response_body
            raise e

    def get_pk(self):
        return getattr(self, self._pk).get()

    def save(self):
        serialized = {}
        for field in self._fields:
            v = getattr(self, field).serialize()
            if v:
                serialized[field] = v

        pk = getattr(self, self._pk).serialize()
        response = None
        data = json.dumps({self._name[0]: serialized})
        if pk:
            response = self._con.request_data("PUT", self._name[1] + "/" + pk, data)
        else:
            response = self._con.request_data("POST", self._name[1], data)

        try:
            newdata = json.loads(response.response_body)
            single = newdata.get(self._name[0], None)
            assert single, "Should return a json with an object of type single"
            for field in self._fields:
                getattr(self, field)._set(single.get(field, None))

        except ValueError, e:
            print self._name[1]
            print response.response_body
            raise e

        return self


