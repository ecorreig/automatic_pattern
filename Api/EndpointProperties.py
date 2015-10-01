__author__ = 'dracks'

from Manager import DataManager
import dateutil.parser
import time


class InterfaceProperty:
    def get(self):
        assert False, "Not implemented function"

    def set(self, value):
        assert False, "Not implemented function"

    def serialize(self):
        assert False, "Not implemented function"


class AbstractDataType(InterfaceProperty):
    def __init__(self, name):
        self._name = name
        self.__model = None
        self.cache = None
        self.value = None

    def instantiate(self, value):
        new = self.__class__(self._name)
        new._set(value)
        return new

    def _set(self, value):
        # print value, self.value
        self.cache = None
        self.value = value

    def serialize(self):
        return self.value


class Property(InterfaceProperty):
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def _set(self, value):
        self.value = value

    def get(self):
        return self.value

    def serialize(self):
        return self.value


class DateProperty(Property):
    def __init__(self, value=None):
        Property.__init__(self, value)

    def instantiate(self, value):
        if value is not None and value != "0000-00-00":
            return DateProperty(dateutil.parser.parse(value))
        else:
            return DateProperty()

    def serialize(self):
        if self.value is not None:
            return self.value.isoformat()
        else:
            return None


class BooleanProperty(Property):
    def __init__(self, value=None):
        Property.__init__(self, value)

    def instantiate(self, value):
        b = False
        if isinstance(value, str) or isinstance(value, unicode):
            if value.lower() == 'true':
                b = True
        elif isinstance(value, bool):
            b = value
        return BooleanProperty(b)

    def serialize(self):
        if self.value is not None:
            if self.value:
                return "true"
            else:
                return "false"
        else:
            return None


class HasMany(AbstractDataType):
    def __init__(self, name):
        AbstractDataType.__init__(self, name)
        self.value = []

    def get(self):
        assert self.value is not None, "Instance not initialized"
        if self.cache is None:
            manager = DataManager.sharedManager()
            name = self._name
            self.cache = map(lambda e: manager.retrieve(name, e), self.value)

        return self.cache

    def set(self, list_objects):
        self.cache = list_objects
        self.value = map(lambda e: e.get_pk(), self.cache)

    def serialize(self):
        if self.cache is not None:
            self.value = map(lambda e: e.get_pk(), self.cache)
            return self.value
        else:
            return self.value


class BelongsTo(AbstractDataType):
    def __init__(self, name):
        AbstractDataType.__init__(self, name)

    def get(self):
        if self.cache is None:
            if self.value is None:
                return None
            manager = DataManager.sharedManager()
            name = self._name
            self.cache = manager.retrieve(name, self.value)

        return self.cache

    def set(self, object):
        self.cache = object
        if object:
            self.value = object.get_pk()
        else:
            self.value = None
