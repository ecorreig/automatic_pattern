__author__ = 'dracks'

import json

class Model:
    _name = None
    _fields = []
    _con = None

    def __init__(self, data):
        for field in self._fields:
            if hasattr(self, field):
                attr = getattr(self, field)
                setattr(self, field, attr.instantiate(data[field]))
            else:
                setattr(self, field, data[field])

    @classmethod
    def get(cls, request=None, query=None):
        call=cls._name[1]
        if request is not None:
            call=call+"/"+request
        r = cls._con.request_data("GET", call, "")
        try :
            data = json.loads(r.response_body)
            single = data.get(cls._name[0], None)
            if single is None:
                data = data.get(cls._name[1], None)
                assert(data is not None)
                return map(cls, data)
            else:
                return cls(single)
        except ValueError, e:
            print call
            print r.response_body
            raise e