__author__ = 'dracks'

from Manager import DataManager


class Property:
    def __init__(self, name):
        self.__name = name
        self.__model = None
        self.cache = None
        self.value = None

    def instantiate(self, value):
        new = self.__class__(self.__name)
        new.value = value
        return new

    def _getModel(self):
        if self.__model is None:
            self.__model = DataManager.get(self.__name)
        return self.__model

    def set(self, value):
        print value, self.value
        self.cache = None
        self.value = value

    def get(self):
        assert False, "Not implemented function"


class HasMany(Property):
    def __init__(self, name):
        Property.__init__(self, name)
        self.value = []

    def get(self):
        assert self.value is not None, "Instance not initialized"
        if self.cache is None:
            model = self._getModel()
            self.cache = map(lambda e: model.get(e), self.value)

        return self.cache

class BelongsTo(Property):
    def __init__(self, name):
        Property.__init__(self, name)

    def get(self):
        assert self.value is not None, "Instance not initialized"
        if self.cache is None:
            self.cache=self._getModel().get(self.value)

        return self.cache