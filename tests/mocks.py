__author__ = 'dracks'

import create_warnings


class MockSession:
    list_sessions = []
    get_args = {}

    def __init__(self, model=None, status_begin=None, status_end=None, difficulty=None, publish_date=None,
                 completed_time=None):
        self.model_based = model
        self.publish_date = publish_date
        self.completed_time = completed_time
        self.status_begin = status_begin
        self.status_end = status_end
        self.difficulty = difficulty

    @classmethod
    def get(cls, **args):
        cls.get_args = args
        return cls.list_sessions

    def save(self):
        pass


class MockOlderConfig:
    get_value = []
    get_count = 0

    save_count = 0

    def __init__(self, working_days=None, warnings=None):
        if warnings is None:
            warnings = []
        self.workingDays = working_days
        self.pattern = None
        self.level = None
        self.warnings = warnings
        self.older = None
        self.lastLevel = None
        self.lastBlock = None

    @classmethod
    def get(cls):
        cls.get_count += 1
        return cls.get_value

    def save(self):
        self.save_count += 1

    def get_list_block_session(self):
        blocks_session = filter(lambda e: e.level == self.level, self.block.sessions)
        if self.lastBlock:
            blocks_session.extend(filter(lambda e: e.level == self.lastLevel, self.lastBlock.sessions))
        return blocks_session


class MockWarning:
    retrieve_value = None
    retrieve_count = 0
    code_list = []

    def __init__(self, code=None):
        self.code = code

    @classmethod
    def load(cls):
        old_create = create_warnings.create

        def mock_create(code, level, label_ca, label_es):
            cls.code_list.append(code)

        create_warnings.create = mock_create
        create_warnings.insert()
        create_warnings.create = old_create

    @classmethod
    def retrieve(cls, code):
        cls.retrieve_count += 1
        if cls.retrieve_value:
            return cls.retrieve_value
        else:
            return MockWarning(code)


class MockPatternHistory:
    list_mocks = []

    def __init__(self):
        pass

    def save(self):
        MockPatternHistory.list_mocks.append(self)
