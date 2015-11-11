__author__ = 'dracks'
import unittest
import models
from Api.Manager import DataManager
import main
import dateutil.parser
import datetime

import models_tests
import mocks


class DayWeekTests(unittest.TestCase):
    def test_sunday(self):
        day = dateutil.parser.parse("2015-09-27")
        self.assertEqual(main.day_week(day), 'sunday')

    def test_monday(self):
        day = dateutil.parser.parse("2015-09-21")
        self.assertEqual(main.day_week(day), 'monday')


class WeekStartDateTests(unittest.TestCase):
    def test_monday(self):
        day = "2015-09-28"
        monday = dateutil.parser.parse(day)
        self.assertEqual(monday, main.week_start_date(monday))

    def test_sunday(self):
        monday = dateutil.parser.parse("2015-09-21")
        day = dateutil.parser.parse("2015-09-27")
        self.assertEqual(monday, main.week_start_date(day))


class GetFilteredTimesTests(unittest.TestCase):
    def test_server_response_copy(self):
        activity = models.Activity()
        activity.sort = "100"
        activity.times = "125,167,140,140,128,128,141,128,128,143,127,129,129,129,142,116,127,269"
        session = models_tests.generate_session(activities=[activity])
        deleted, words_minute = main.get_filtered_times(session)
        self.assertEqual(deleted, 1)
        self.assertEqual(int(words_minute*1000), 449933)

    def test_activities_sort(self):
        a = models.Activity()
        a.sort = "20"
        a.times = "1,2,3,2,1,2,3"
        a2 = models.Activity()
        a2.sort = "100"
        a2.times = "1,1,1,1,2,2,2,2,8,10"
        deleted, words_minute = main.get_filtered_times(models_tests.generate_session(activities=[a, a2]))
        self.assertEqual(deleted, 2)
        self.assertEqual(words_minute, 60*1000/1.5)


class GetPercentileTest(unittest.TestCase):
    def setUp(self):
        self.percentiles = []
        this = self

        self.get_filtered_times_value = (0,0)
        self.get_filtered_times_last_session = None
        self.mock_get_filtered_times = main.get_filtered_times

        def mock_retrieve_all(model):
            return this.percentiles

        def mock_get_filtered_times(session):
            self.get_filtered_times_last_session = session
            return self.get_filtered_times_value

        main.get_filtered_times = mock_get_filtered_times

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

    def tearDown(self):
        main.get_filtered_times = self.mock_get_filtered_times

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
        activity1.sort = 10
        activity1.words_minute = 10
        activity2 = models.Activity()
        activity2.sort = 20
        activity2.words_minute = 19
        session.list_activities = [
            activity2, activity1
        ]

        self.assertIsNone(main.get_percentile(self.mock_older, session))
        session.model_based = self.model_session2
        self.assertIsNone(main.get_percentile(self.mock_older, session))
        self.get_filtered_times_value = (0,19)

        self.mock_older.group.course.id = 6
        r = main.get_percentile(self.mock_older, session)
        self.assertEqual(self.get_filtered_times_last_session, session)
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
        self.assertEqual(self.configuration.session, sessions[0])

    def test_repeat(self):
        bj = models.BlockJumpDefault()
        bj.repeatBlock = True
        bj.nextLevel = 3
        self.configuration.block = self.b1
        main.jump(self.configuration, bj)
        self.assertEqual(self.configuration.block, self.b1)
        self.assertEqual(self.configuration.level, 3)
        sessions = filter(lambda e: e.level == 3, self.b1.sessions)
        self.assertEqual(self.configuration.session, sessions[0])

    def test_save_old(self):
        self.configuration.block = self.b1
        self.configuration.level = 1

        bj = models.BlockJumpCondition()
        bj.repeatBlock = False
        bj.nextLevel = 2

        main.jump(self.configuration, bj)
        self.assertEqual(self.configuration.lastBlock, self.b1)
        self.assertEqual(self.configuration.lastLevel, 1)


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
        self.warnings = models.Warnings
        models.Warnings = mocks.MockWarning

        self.bjc = models_tests.generate_block_jump_condition(level="1")
        bjc2 = models_tests.generate_block_jump_condition(level="1")
        self.bjd = models_tests.generate_block_jump_default(level="2")
        bj = models_tests.generate_block_jump(conditions=[self.bjc, bjc2], defaults=[self.bjd])
        self.configuration = models.OlderConfig()
        self.configuration.warnings = []
        self.configuration.level = "1"
        self.list_sessions = [
            models_tests.generate_block_session(order=10, level="1"),
            models_tests.generate_block_session(order=20, level="1"),
            models_tests.generate_block_session(order=15, level="1"),
            models_tests.generate_block_session(order=10, level="2"),
            models_tests.generate_block_session(order=20, level="3"),
            models_tests.generate_block_session(order=10, level="3")

        ]
        self.block = models_tests.generate_block(block_jump=bj, sessions=self.list_sessions)
        self.configuration.block = self.block

    def tearDown(self):
        main.get_average_data = self.get_average_data
        main.jump = self.jump

    def test_next_session(self):
        self.configuration.session = self.list_sessions[2]
        self.configuration.level = "1"
        main.update_config(self.configuration, [], [])
        self.assertEqual(self.configuration.session, self.list_sessions[1])

    def test_with_found_average(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None
        self.mock_avg_percentile = 0
        self.configuration.session = self.list_sessions[1]
        self.configuration.level = 1
        main.update_config(self.configuration, [], [])
        self.assertEqual(self.last_jump_configuration, self.configuration)
        self.assertEqual(self.last_jump_condition, self.bjc)

    def test_with_not_found_average(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None
        self.mock_avg_percentile = None
        self.configuration.session = self.list_sessions[3]
        self.configuration.level = 2
        self.configuration.block = self.block
        main.update_config(self.configuration, [], [])
        self.assertEqual(self.last_jump_configuration, self.configuration)
        self.assertEqual(self.last_jump_condition, self.bjd)

    def test_with_not_found_anything(self):
        self.last_jump_configuration = None
        self.last_jump_condition = None
        self.mock_avg_percentile = None
        self.configuration.session = self.list_sessions[4]
        self.configuration.level = 3
        self.configuration.block = self.block
        main.update_config(self.configuration, [], [])
        self.assertEqual(self.last_jump_configuration, None)
        self.assertEqual(self.last_jump_condition, None)
        self.assertEqual(self.configuration.session, self.list_sessions[5])

    def test_with_not_block_jump(self):
        mock_warning = mocks.MockWarning()
        mocks.MockWarning.retrieve_value = mock_warning
        self.configuration.block = models_tests.generate_block(sessions=self.list_sessions)
        self.configuration.session = self.list_sessions[1]
        main.update_config(self.configuration, [], [])
        self.assertEqual(self.configuration.session, self.list_sessions[0])
        self.assertEqual(len(self.configuration.warnings), 1)
        self.assertEqual(self.configuration.warnings[0], mock_warning)


class PautaTests(unittest.TestCase):
    def test(self):
        mock_session = mocks.MockSession()
        configuration = mocks.MockOlderConfig()
        configuration.session = models_tests.generate_block_session(session=mock_session)
        session = main.pauta(configuration)
        self.assertEqual(session.student, configuration.older)
        self.assertEqual(session.publish_date.date(), datetime.date.today())
        self.assertEqual(session.model_based, mock_session)


class GetCountersTests(unittest.TestCase):
    def setUp(self):
        self.days = map(lambda e: dateutil.parser.parse("2015/09/" + str(e)), range(21, 28))
        self.model_sessions = [
            models_tests.generate_model_session(),
            models_tests.generate_model_session(),
            models_tests.generate_model_session()
        ]

    def test(self):
        list = [
            mocks.MockSession(self.model_sessions[0], publish_date=None, completed_time=self.days[0]),
            mocks.MockSession(self.model_sessions[0], publish_date=self.days[1], completed_time=self.days[2]),
            mocks.MockSession(models_tests.generate_model_session(), publish_date=self.days[0],
                              completed_time=self.days[0]),
            mocks.MockSession(self.model_sessions[0], publish_date=self.days[2], completed_time=self.days[2]),
            mocks.MockSession(models_tests.generate_model_session(), publish_date=self.days[2],
                              completed_time=self.days[2]),
            mocks.MockSession(self.model_sessions[1], publish_date=self.days[3], completed_time=self.days[3]),
            mocks.MockSession(models_tests.generate_model_session(), publish_date=self.days[4], completed_time=None),
            mocks.MockSession(self.model_sessions[2], publish_date=self.days[5], completed_time=None),
        ]
        not_done, not_done_pattern, s_week = main.get_counters(list, self.model_sessions, self.days[2])
        self.assertEqual(not_done, 2)
        self.assertEqual(not_done_pattern, 1)
        self.assertEqual(s_week, 3)


class GenerateLists(unittest.TestCase):
    def setUp(self):
        self.older_config_get_list_block_session = mocks.MockOlderConfig.get_list_block_session
        self.older_config_get_current_block_session = mocks.MockOlderConfig.get_current_block_session
        self.older_config_get_list_block_session_value = []
        self.older_config_get_current_block_Session_value = []

        this = self

        def mock_get_list_block_session(self):
            return this.older_config_get_list_block_session_value

        def mock_get_current_block_session(self):
            return this.older_config_get_current_block_Session_value

        mocks.MockOlderConfig.get_list_block_session = mock_get_list_block_session
        mocks.MockOlderConfig.get_current_block_session = mock_get_current_block_session

    def tearDown(self):
        mocks.MockOlderConfig.get_list_block_session = self.older_config_get_list_block_session
        mocks.MockOlderConfig.get_current_block_session = self.older_config_get_current_block_session

    def test_global(self):
        models_session = [
            models_tests.generate_model_session(),
            models_tests.generate_model_session(),
            models_tests.generate_model_session()
        ]
        self.older_config_get_list_block_session_value = [
            models_tests.generate_block_session(session=models_session[0], use_data=False),
            models_tests.generate_block_session(session=models_session[1], use_data=False),
            models_tests.generate_block_session(session=models_session[2], use_data=True)
        ]
        self.older_config_get_current_block_Session_value = self.older_config_get_list_block_session_value
        configuration = mocks.MockOlderConfig()
        sessions = [
            mocks.MockSession(model=models_session[0], status_begin=5,
                              completed_time=dateutil.parser.parse("2015-09-21")),
            mocks.MockSession(model=models_session[1], status_begin=5,
                              completed_time=dateutil.parser.parse("2015-09-21")),
            mocks.MockSession(model=models_tests.generate_model_session(),
                              status_begin=5, completed_time=dateutil.parser.parse("2015-09-21")),
            mocks.MockSession(model=models_session[2], status_begin=5, completed_time=None),
            mocks.MockSession(model=models_tests.generate_model_session(), completed_time=None),
        ]
        list_sessions, sessions_made, sessions_use_data = main.generate_lists(configuration,
                                                                              sessions)
        self.assertEqual(list_sessions, models_session)
        self.assertEqual(sessions_made, [sessions[0], sessions[1]])
        self.assertEqual(sessions_use_data, [models_session[2]])


class CheckWarningsTests(unittest.TestCase):
    def setUp(self):
        mocks.MockWarning.load()
        self.append_warning = main.append_warning
        self.append_warning_code_list = []
        self.get_filtered_times = main.get_filtered_times
        self.get_filtered_times_last_session = None
        self.get_filtered_times_value = (0, 0)
        self.get_percentile = main.get_percentile
        self.get_percentile_value = None

        def mock_append_warning(configuration, code):
            self.assertTrue(code in mocks.MockWarning.code_list)
            self.append_warning_code_list.append(code)

        def mock_get_filtered_times(session):
            self.get_filtered_times_last_session = session
            return self.get_filtered_times_value

        def mock_get_percentile(older, session):
            return self.get_percentile_value

        main.append_warning = mock_append_warning
        main.get_filtered_times = mock_get_filtered_times
        main.get_percentile = mock_get_percentile

        self.sessions = [
            mocks.MockSession(status_begin="7", status_end=7, difficulty=8,
                              completed_time=dateutil.parser.parse("2015-09-21 20:00+02:00")),
            mocks.MockSession(status_begin="7", status_end=7, difficulty=8,
                              completed_time=dateutil.parser.parse("2015-09-22 20:00+02:00")),
            mocks.MockSession(status_begin="7", status_end=7, difficulty=8,
                              completed_time=dateutil.parser.parse("2015-09-23 20:00+02:00")),
            mocks.MockSession(status_begin="7", status_end=7, difficulty=8,
                              completed_time=dateutil.parser.parse("2015-09-24 20:00+02:00")),
            mocks.MockSession(status_begin="7", status_end=7, difficulty=8,
                              completed_time=dateutil.parser.parse("2015-09-25 20:00+02:00")),
        ]
        self.configuration = mocks.MockOlderConfig()
        self.configuration.numberSessions = 2

    def tearDown(self):
        main.append_warning = self.append_warning
        main.get_filtered_times = self.get_filtered_times
        main.get_percentile = self.get_percentile

    def test_avg_low_mot(self):
        # self.get_filtered_times_value = (0, 0)
        self.get_percentile_value = 10
        self.sessions[-1].status_begin = 0
        self.sessions[-2].status_begin = 0
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-1.1")

        self.sessions[-1].status_begin = 4
        self.sessions[-2].status_begin = 4
        self.append_warning_code_list = []
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-1.4")

        self.sessions[-1].status_begin = 4
        self.sessions[-2].status_begin = 5
        self.append_warning_code_list = []
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-1.3")

        self.sessions[-1].status_begin = 6
        self.sessions[-2].status_begin = 6
        self.sessions[-3].status_begin = 5
        self.sessions[-4].status_begin = 6
        self.append_warning_code_list = []

        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-1.2")

    def test_mot_difference(self):
        # self.get_filtered_times_value = (0, 0)
        self.sessions[-1].status_end = int(self.sessions[-1].status_begin) - 1
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-3.3")

        self.append_warning_code_list = []
        self.sessions[-1].status_end = int(self.sessions[-1].status_begin) - 4
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-3.2")

        self.append_warning_code_list = []
        self.sessions[-1].status_end = int(self.sessions[-1].status_begin) - 4
        self.sessions[-2].status_end = int(self.sessions[-2].status_begin) - 4
        self.sessions[-3].status_end = int(self.sessions[-3].status_begin) - 5
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "MOT-3.1")

    def test_filtered_times(self):
        self.get_filtered_times_value = (1, 0)
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "CL-1.3")

        self.append_warning_code_list = []
        self.get_filtered_times_value = (3, 0)
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "CL-1.2")

        self.append_warning_code_list = []
        self.get_filtered_times_value = (3, 0)
        self.sessions[-1].status_end = int(self.sessions[-1].status_begin) - 4
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 2)
        self.assertEqual(self.append_warning_code_list[1], "CL-1.1")

    def test_percentile(self):
        self.get_percentile_value = 3
        self.sessions[-1].difficulty = 3
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "CL-2.1")

    def test_time(self):
        self.sessions[-1].completed_time = dateutil.parser.parse("2015-09-30 20:59:59+02:00")
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 0)

        self.sessions[-1].completed_time = dateutil.parser.parse("2015-09-30 21:00:01+02:00")
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "H-1.1")

        self.append_warning_code_list = []
        self.sessions[-1].completed_time = dateutil.parser.parse("2015-09-30 06:59:59+02:00")
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "H-1.1")

        self.append_warning_code_list = []
        self.sessions[-1].completed_time = dateutil.parser.parse("2015-09-30 07:00:00+02:00")
        main.check_warnings(self.configuration, [], self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 0)

    def test_not_done(self):
        sessions = []
        for session in self.sessions:
            session.publish_date = dateutil.parser.parse("2015-09-21")
            sessions.append(session)

        sessions.append(mocks.MockSession(publish_date=dateutil.parser.parse("2015-09-22")))
        main.check_warnings(self.configuration, sessions, self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 0)

        sessions.append(mocks.MockSession(publish_date=dateutil.parser.parse("2015-09-22")))
        main.check_warnings(self.configuration, sessions, self.sessions)
        self.assertEqual(len(self.append_warning_code_list), 1)
        self.assertEqual(self.append_warning_code_list[0], "S-1.1")


class RunTests(unittest.TestCase):
    def setUp(self):
        self.pauta = main.pauta
        self.update_config = main.update_config
        self.session = models.Session
        self.pattern_history = models.PatternHistory
        self.get_counters = main.get_counters
        self.configuration_save = models.OlderConfig.save
        self.check_warnings = main.check_warnings
        self.last_check_warnings_sessions = None
        self.last_check_warnings_all_sessions = None
        self.count = {
            "pauta": 0,
            "update_config": 0,
            "get_counters": 0,
        }
        self.list_sessions = []
        self.get_counters_value = (0, 0, 0)

        def mock_pauta(configuration):
            self.count["pauta"] += 1
            return mocks.MockSession()

        def mock_update_config(configuration, sessions_made, sessions_use_data):
            self.count["update_config"] += 1

        def mock_get_counters(sessions, list_sessions, monday):
            self.count["get_counters"] += 1
            return self.get_counters_value

        def mock_check_warnings(configuration, all_sessions, sessions):
            self.last_check_warnings_sessions = sessions
            self.last_check_warnings_all_sessions = all_sessions

        models.Session = mocks.MockSession
        models.PatternHistory = mocks.MockPatternHistory
        main.pauta = mock_pauta
        main.update_config = mock_update_config
        main.get_counters = mock_get_counters
        main.check_warnings = mock_check_warnings

        self.configuration = mocks.MockOlderConfig()
        self.configuration.block = models_tests.generate_block(sessions=[])
        self.configuration.older = models.Older()
        self.configuration.older.id = 1
        self.configuration.level = "1"
        self.configuration.numberSessions = 2
        self.configuration.maxSessionsWeek = 5

    def tearDown(self):
        main.pauta = self.pauta
        main.update_config = self.update_config
        models.Session = self.session
        main.get_counters = self.get_counters
        models.OlderConfig.save = self.configuration_save
        main.check_warnings = self.check_warnings
        models.PatternHistory = self.pattern_history

    def test_normal_state(self):
        main.run(self.configuration, "monday")
        self.assertEqual(self.count['pauta'], 2)
        self.assertEqual(self.count['update_config'], 2)
        self.assertEqual(self.count['get_counters'], 1)
        self.assertEqual(mocks.MockSession.get_args['query'], 'student=1&count=20')

    def test_max_sessions_week(self):
        self.get_counters_value = (0, 0, 4)
        self.configuration.older.id = 3
        main.run(self.configuration, "monday")
        self.assertEqual(self.count['pauta'], 1)
        self.assertEqual(mocks.MockSession.get_args['query'], 'student=3&count=20')

    def test_max_sessions(self):
        self.get_counters_value = (9, 0, 0)
        main.run(self.configuration, "monday")
        self.assertEqual(self.count['pauta'], 1)
        self.assertEqual(mocks.MockSession.get_args['query'], 'student=1&count=20')

    def test_sessions(self):
        self.get_counters_value = (0, 3, 0)
        main.run(self.configuration, "monday")
        self.assertEqual(self.count['pauta'], 1)
        self.assertEqual(mocks.MockSession.get_args['query'], 'student=1&count=20')

    def test_no_max_sessions_week(self):
        self.configuration.maxSessionsWeek = None
        self.get_counters_value = (0, 0, 4)
        main.run(self.configuration, "monday")
        self.assertEqual(self.count['pauta'], 2)
        self.assertEqual(self.count['update_config'], 2)
        self.assertEqual(self.count['get_counters'], 1)

    def test_history(self):
        self.get_counters_value = (0, 0, 0)
        mocks.MockPatternHistory.list_mocks = []
        self.configuration.pattern = models_tests.generate_pattern()
        self.configuration.block = models_tests.generate_block()
        self.configuration.level = 2
        self.configuration.older = models.Older()
        self.configuration.warnings = [mocks.MockWarning(), mocks.MockWarning()]
        main.run(self.configuration, "monday")
        self.assertEqual(len(mocks.MockPatternHistory.list_mocks), 1)
        historic = mocks.MockPatternHistory.list_mocks[0]
        self.assertEqual(self.configuration.pattern, historic.pattern)
        self.assertEqual(self.configuration.block, historic.block)
        self.assertEqual(self.configuration.level, historic.level)
        self.assertEqual(self.configuration.older, historic.older)
        self.assertEqual(self.configuration.warnings, historic.warnings)
        self.assertEqual(len(historic.sessions), 2)


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
