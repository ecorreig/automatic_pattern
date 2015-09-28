__author__ = 'dracks'


class MockSession:
    list_sessions = []

    def __init__(self, publish_date=None, completed_time=None):
        self.publish_date = publish_date
        self.completed_time = completed_time

    @classmethod
    def get(cls):
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
