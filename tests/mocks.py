__author__ = 'dracks'


class MockSession:
    list_sessions = []
    get_args = {}

    def __init__(self, model=None, publish_date=None, completed_time=None):
        self.model_based=model
        self.publish_date = publish_date
        self.completed_time = completed_time

    @classmethod
    def get(cls, **args):
        cls.get_args = args
        return cls.list_sessions

    def save(self):
        pass


class MockOlderConfig:
    get_value = []

    def __init__(self, working_days):
        self.workingDays = working_days

    @classmethod
    def get(cls):
        return cls.get_value
