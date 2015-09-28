__author__ = 'dracks'
import unittest
import models
from Api.Manager import DataManager
import main
import dateutil.parser
import datetime

import models_tests
import mocks


class DayWeekTest(unittest.TestCase):
    def test_sunday(self):
        day = dateutil.parser.parse("2015-09-27")
        self.assertEqual(main.day_week(day), 'sunday')

    def test_monday(self):
        day = dateutil.parser.parse("2015-09-21")
        self.assertEqual(main.day_week(day), 'monday')


class WeekStartDateTest(unittest.TestCase):
    def test_monday(self):
        day = "2015-09-28"
        monday = dateutil.parser.parse(day)
        self.assertEqual(monday, main.week_start_date(monday))

    def test_sunday(self):
        monday = dateutil.parser.parse("2015-09-21")
        day = dateutil.parser.parse("2015-09-27")
        self.assertEqual(monday, main.week_start_date(day))


class GetPercentileTest(unittest.TestCase):
    def setUp(self):
        self.percentiles = []
        this = self

        def mock_retrieve_all(model):
            return this.percentiles

        DataManager.sharedManager().retrieve_all = mock_retrieve_all
        self.mock_older = models.Older()
        self.mock_older.group = models.Group()
        mock_course = models.Course()
        mock_course.id = 2
        self.mock_older.group.course = mock_course

        self.model_session1 = models.ModelSession()
        self.model_session1.type_percentile = 1

        self.model_session2 = models.ModelSession()
        self.model_session2.type_percentile = 4

    def test_get_not_valid(self):
        session1 = models.Session()
        session1.completed_time = dateutil.parser.parse('2015-08-01')
        session1.model_based = self.model_session1
        self.percentiles = []

        self.assertIsNone(main.get_percentile(self.mock_older, session1))

    def test_get_multiple_percentiles(self):
        date = dateutil.parser.parse('2015-08-01')
        trimester = main.get_trimester(date)
        session = models.Session()
        session.completed_time = date
        session.model_based = self.model_session1
        list_percentiles = []

        for i in range(0, 10):
            list_percentiles.append(models_tests.generate_percentile(
                pk=i, seed=5, type=i * 2, course=i * 3, trimester=trimester
            ))
        self.percentiles = list_percentiles

        activity1 = models.Activity()
        activity1.order = 10
        activity1.words_minute = 10
        activity2 = models.Activity()
        activity2.order = 20
        activity2.words_minute = 19
        session.list_activities = [
            activity2, activity1
        ]

        self.assertIsNone(main.get_percentile(self.mock_older, session))
        session.model_based = self.model_session2
        self.assertIsNone(main.get_percentile(self.mock_older, session))

        self.mock_older.group.course.id = 6
        r = main.get_percentile(self.mock_older, session)
        self.assertIsNotNone(r)
        self.assertEqual(r, 20)


class GetAverageDataTest(unittest.TestCase):
    def setUp(self):
        self.get_percentile = main.get_percentile

    def tearDown(self):
        main.get_percentile = self.get_percentile

    def test_no_data(self):
        p, m = main.get_average_data(None, [], [])
        self.assertIsNone(p)
        self.assertIsNone(m)

    def test_with_data(self):
        self.tmp = 0

        def mock_get_percentile(older, session):
            self.tmp += 1
            return self.tmp

        main.get_percentile = mock_get_percentile

        ms1 = models_tests.generate_model_session(1)
        ms2 = models_tests.generate_model_session(2)
        ms3 = models_tests.generate_model_session(3)

        sessions = [
            models_tests.generate_session(model=ms1),
            models_tests.generate_session(model=ms1),
            models_tests.generate_session(model=ms1)
        ]

        p, m = main.get_average_data(None, sessions, [ms2, ms3])
        self.assertIsNone(p)
        self.assertIsNone(m)

        sessions = [
            models_tests.generate_session(model=ms1, motivation=1),
            models_tests.generate_session(model=ms2),
            models_tests.generate_session(model=ms3)
        ]
        p, m = main.get_average_data(None, sessions, [ms1])
        self.assertEqual(p, 1)
        self.assertEqual(m, 1)

        sessions = [
            models_tests.generate_session(model=ms1, motivation=1),
            models_tests.generate_session(model=ms2, motivation=5),
            models_tests.generate_session(model=ms3)
        ]
        p, m = main.get_average_data(None, sessions, [ms1, ms2])
        self.assertEqual(p, 2.5)
        self.assertEqual(m, 3)


class JumpTests(unittest.TestCase):
    def setUp(self):
        def generate_sessions():
            list_mock_sessions = []
            for level in range(1, 5):
                list_mock_sessions.extend([
                    models_tests.generate_block_session(level * 5, level=level, session=models.ModelSession(),
                                                        order=10),
                    models_tests.generate_block_session(level * 5 + 1, level=level, session=models.ModelSession(),
                                                        order=20),
                    models_tests.generate_block_session(level * 5 + 2, level=level, session=models.ModelSession(),
                                                        order=30),
                ])
            return list_mock_sessions

        self.configuration = models.OlderConfig()
        self.b1 = models_tests.generate_block(order=10, sessions=generate_sessions())
        self.b2 = models_tests.generate_block(order=20, sessions=generate_sessions())
        self.b3 = models_tests.generate_block(order=30, sessions=generate_sessions())
        self.configuration.pattern = models_tests.generate_pattern(blocks=[self.b1, self.b3, self.b2])

    def test_not_repeat(self):
        self.configuration.block = self.b1
        bj = models.BlockJumpDefault()
        bj.repeatBlock = False
        bj.nextLevel = 2
        main.jump(self.configuration, bj)
        self.assertEqual(self.configuration.block, self.b2)
        self.assertEqual(self.configuration.level, 2)
        sessions = filter(lambda e: e.level == 2, self.b2.sessions)
        self.assertEqual(self.configuration.session, sessions[0].session)

    def test_repeat(self):
        bj = models.BlockJumpDefault()
        bj.repeatBlock = True
        bj.nextLevel = 3
        self.configuration.block = self.b1
        main.jump(self.configuration, bj)
        self.assertEqual(self.configuration.block, self.b1)
        self.assertEqual(self.configuration.level, 3)
        sessions = filter(lambda e: e.level == 3, self.b1.sessions)
        self.assertEqual(self.configuration.session, sessions[0].session)


class UpdateConfigTests(unittest.TestCase):
    def setUp(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None

        self.mock_avg_percentile = None
        self.mock_avg_motivation = None

        def mock_jump(configuration, condition):
            self.last_jump_configuration = configuration
            self.last_jump_condition = condition

        def mock_get_average_data(older, s1, s2):
            return self.mock_avg_percentile, self.mock_avg_motivation

        self.get_average_data = main.get_average_data
        main.get_average_data = mock_get_average_data
        self.jump = main.jump
        main.jump = mock_jump

        self.bjc = models_tests.generate_block_jump_condition(level=1)
        bjc2 = models_tests.generate_block_jump_condition(level=1)
        self.bjd = models_tests.generate_block_jump_default(level=2)
        bj = models_tests.generate_block_jump(conditions=[self.bjc, bjc2], defaults=[self.bjd])
        self.configuration = models.OlderConfig()
        self.list_sessions = [
            models_tests.generate_model_session(),
            models_tests.generate_model_session(),
            models_tests.generate_model_session()
        ]
        self.block = models_tests.generate_block(block_jump=bj, sessions=self.list_sessions)
        self.configuration.block = self.block

    def tearDown(self):
        main.get_average_data = self.get_average_data
        main.jump = self.jump

    def test_next_session(self):
        self.configuration.session = self.list_sessions[1]
        main.update_config(self.configuration, self.list_sessions, [], [])
        self.assertEqual(self.configuration.session, self.list_sessions[2])

    def test_with_found_average(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None
        self.mock_avg_percentile = 0
        self.configuration.session = self.list_sessions[2]
        self.configuration.level = 1
        main.update_config(self.configuration, self.list_sessions, [], [])
        self.assertEqual(self.last_jump_configuration, self.configuration)
        self.assertEqual(self.last_jump_condition, self.bjc)

    def test_with_not_found_average(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None
        self.mock_avg_percentile = None
        self.configuration.session = self.list_sessions[2]
        self.configuration.level = 2
        self.configuration.block = self.block
        main.update_config(self.configuration, self.list_sessions, [], [])
        self.assertEqual(self.last_jump_configuration, self.configuration)
        self.assertEqual(self.last_jump_condition, self.bjd)

    def test_with_not_found_anything(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None
        self.mock_avg_percentile = None
        self.configuration.session = self.list_sessions[2]
        self.configuration.level = 3
        self.configuration.block = self.block
        main.update_config(self.configuration, self.list_sessions, [], [])
        self.assertEqual(self.last_jump_configuration, None)
        self.assertEqual(self.last_jump_condition, None)
        self.assertEqual(self.configuration.session, self.list_sessions[0])

    def test_with_not_block_jump(self):
        self.configuration.block = models_tests.generate_block(sessions=self.list_sessions)
        self.configuration.session = self.list_sessions[2]
        main.update_config(self.configuration, self.list_sessions, [], [])
        self.assertEqual(self.configuration.session, self.list_sessions[0])


class RunTests(unittest.TestCase):
    def setUp(self):
        self.pauta = main.pauta
        self.update_config = main.update_config
        self.session = models.Session
        self.count = {
            "pauta": 0,
            "update_config": 0,
            "session_get": 0,
            "session_save": 0
        }
        self.list_sessions = []

        def mock_pauta(configuration):
            self.count["session_get"] += 1
            return mocks.MockSession()

        def mock_update_config(configuration, list_sessions, sessions_made, sessions_use_data):
            self.count["update_config"] += 1

        models.Session = mocks.MockSession
        main.pauta = mock_pauta
        main.update_config = mock_update_config

    def tearDown(self):
        main.pauta = self.pauta
        main.update_config = self.update_config
        models.Session = self.session


class MainTest(unittest.TestCase):
    def setUp(self):
        self.older_config = models.OlderConfig
        self.run = main.run

        self.run_count = 0
        self.run_configurations = []
        self.run_mondais = []

        def mock_run(configuration, day):
            self.run_configurations.append(configuration)
            self.run_mondais.append(day)

        models.OlderConfig = mocks.MockOlderConfig
        main.run = mock_run

        monday = models_tests.generate_working_days(monday=True)
        wednesday = models_tests.generate_working_days(wednesday=True)
        thursday = models_tests.generate_working_days(thursday=True)
        multiple_days = models_tests.generate_working_days(wednesday=True, friday=True)

        mocks.MockOlderConfig.get_value = [
            mocks.MockOlderConfig(working_days=monday),
            mocks.MockOlderConfig(working_days=thursday),
            mocks.MockOlderConfig(working_days=monday),
            mocks.MockOlderConfig(working_days=wednesday),
            mocks.MockOlderConfig(working_days=multiple_days)
        ]

    def tearDown(self):
        models.OlderConfig = self.older_config
        main.run = self.run

    def test_sunday_and_monday(self):
        day = dateutil.parser.parse("2015-09-27")

        main.main(day)
        self.assertEqual(len(self.run_configurations), 0)

        day = dateutil.parser.parse("2015-09-21")
        main.main(day)
        self.assertEqual(len(self.run_configurations), 2)
        self.assertEqual(len(self.run_mondais), 2)
        self.assertEqual(self.run_mondais[0], dateutil.parser.parse("2015-09-21"))

    def test_multiple_days(self):
        day = dateutil.parser.parse("2015-09-23")

        main.main(day)
        self.assertEqual(len(self.run_configurations), 2)
        self.assertEqual(self.run_mondais[0], dateutil.parser.parse("2015-09-21"))

        self.run_configurations = []
        self.run_mondais = []

        day = dateutil.parser.parse("2015-09-25")
        main.main(day)
        self.assertEqual(len(self.run_configurations), 1)
        self.assertEqual(len(self.run_mondais), 1)
        self.assertEqual(self.run_mondais[0], dateutil.parser.parse("2015-09-21"))
