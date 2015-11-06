__author__ = 'dracks'

import unittest
import models
import dateutil.parser
from Api.Manager import DataManager


def generate_working_days(pk=None, monday=False, tuesday=False, wednesday=False, thursday=False, friday=False,
                          saturday=False, sunday=False):
    wd = models.WorkingDays()
    wd.id = pk
    wd.monday = monday
    wd.tuesday = tuesday
    wd.wednesday = wednesday
    wd.thursday = thursday
    wd.friday = friday
    wd.saturday = saturday
    wd.sunday = sunday
    return wd


def generate_older_config(pk=None, pattern=None, working_days=None):
    oc = models.OlderConfig()
    oc.id = pk
    oc.pattern = pattern
    oc.workingDays = working_days
    return oc


def generate_percentile(seed=1, pk=None, type=None, course=None, trimester=None):
    p = models.Percentile()
    p.id = pk
    p.type = type
    p.course = course
    p.semester = trimester
    for i in range(0, 21):
        setattr(p, "p" + str(i * 5), i * seed)
    return p


def generate_model_session(pk=None, type_percentile=None):
    ms = models.ModelSession()
    ms.id = pk
    ms.type_percentile = type_percentile

    return ms


def generate_session(pk=None, model=None, motivation=None, activities=None):
    if activities is None:
        activities = []
    s = models.Session()
    s.id = pk
    s.model_based = model
    s.status_end = motivation
    s.list_activities = activities
    return s


def generate_pattern(pk=None, blocks=None):
    if blocks is None:
        blocks = []
    p = models.Pattern()
    p.id = pk
    p.blocks = blocks
    return p


def generate_block(pk=None, order=None, block_jump=None, sessions=None):
    if sessions is None:
        sessions = []
    b = models.Block()
    b.id = pk
    b.order = order
    b.blockJump = block_jump
    b.sessions = sessions
    return b


def generate_block_session(pk=None, level=None, order=None, session=None, use_data=None):
    bs = models.BlockSession()
    bs.id = pk
    bs.order = order
    bs.level = level
    bs.session = session
    bs.use_data = use_data
    return bs


def generate_block_jump(pk=None, conditions=None, defaults=None):
    if conditions is None:
        conditions = []
    if defaults is None:
        defaults = []

    bj = models.BlockJump()
    bj.id = pk
    bj.conditions = conditions
    bj.defaults = defaults
    return bj


def generate_block_jump_condition(pk=None, level=None, min=None, max=None, mot=None, repeatBlock=None, nextLevel=None,
                                  warning=None):
    bjc = models.BlockJumpCondition()
    bjc.id = pk
    bjc.level = level
    bjc.minPercentile = min
    bjc.maxPercentile = max
    bjc.motivation = mot
    bjc.repeatBlock = repeatBlock
    bjc.nextLevel = nextLevel
    bjc.warning = warning
    return bjc


def generate_block_jump_default(pk=None, level=None, repeatBlock=None, nextLevel=None, warning=None):
    bjd = models.BlockJumpDefault()
    bjd.id = pk
    bjd.level = level
    bjd.repeatBlock = repeatBlock
    bjd.nextLevel = nextLevel
    bjd.warning = warning
    return bjd


class PercentilesTest(unittest.TestCase):
    def setUp(self):
        self.percentile = generate_percentile()

    def test_get_percentile(self):
        subject = self.percentile
        self.assertEqual(subject.get_value(0), 0)
        self.assertEqual(subject.get_value(0.6), 5)
        self.assertEqual(subject.get_value(20), 105)


class OlderTests(unittest.TestCase):
    def setUp(self):
        manager = DataManager.sharedManager()
        manager._cache = {}
        self.retrieve_all = manager.retrieve_all

    def tearDown(self):
        DataManager.sharedManager().retrieve_all = self.retrieve_all

    def test_get_course_birthday(self):
        mock_course = models.Course()
        mock_course.age = 10
        mock_course2 = models.Course()
        mock_course2.age = 11

        def mock_retrieve_all(model):
            return [mock_course, mock_course2]

        manager = DataManager.sharedManager()
        manager.retrieve_all = mock_retrieve_all
        subject = models.Older()
        subject.birthday = dateutil.parser.parse('2008-08-09T15:06:00Z')
        subject.group=models.Group()
        date = dateutil.parser.parse('2018-08-09')
        self.assertEqual(subject.get_course(date), mock_course)
        self.assertEqual(subject.get_course(), None)

    def test_get_course_group(self):
        mock_course = models.Course()
        mock_group = models.Group()
        mock_group.course = mock_course
        subject = models.Older()
        subject.group = mock_group

        self.assertEqual(subject.get_course(), mock_course)


class OlderConfigTests(unittest.TestCase):
    def test_get_list_block_sessions(self):
        older_config = models.OlderConfig()
        current_sessions = [
            generate_block_session(level=1),
            generate_block_session(level=2)
        ]

        older_config.block = generate_block(sessions=current_sessions)
        older_config.level = 1

        old_sessions = [
            generate_block_session(level=3),
            generate_block_session(level=2),
        ]
        older_config.lastBlock = generate_block(sessions=old_sessions)
        older_config.lastLevel = 2
        data = older_config.get_list_block_session()
        self.assertEqual(data, [current_sessions[0], old_sessions[1]])


class BlockJumpConditionTest(unittest.TestCase):
    def setUp(self):
        self.min_percentile = 0
        self.med_percentile = 50
        self.max_percentile = 100

    def test_no_percentile(self):
        subject = models.BlockJumpCondition()
        self.assertTrue(subject.check(self.min_percentile, 0))
        self.assertTrue(subject.check(self.med_percentile, 0))
        self.assertTrue(subject.check(self.max_percentile, 0))

    def test_only_med(self):
        subject = models.BlockJumpCondition()
        subject.minPercentile = "30"
        subject.maxPercentile = 60
        self.assertFalse(subject.check(self.min_percentile, 0))
        self.assertFalse(subject.check(self.max_percentile, 0))
        self.assertTrue(subject.check(self.med_percentile, 0))

    def test_margins(self):
        subject = models.BlockJumpCondition()
        subject.minPercentile = 30
        subject.maxPercentile = 60
        self.assertFalse(subject.check(subject.minPercentile - 1, 0))
        self.assertTrue(subject.check(subject.minPercentile, 0))
        self.assertTrue(subject.check(subject.maxPercentile - 1, 0))
        self.assertFalse(subject.check(subject.maxPercentile, 0))
