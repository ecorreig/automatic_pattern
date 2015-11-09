from dateutil import tz

__author__ = 'dracks'

import models
from Api.Manager import DataManager
from datetime import date, datetime, timedelta, time
import sys
import traceback
import numpy as np
# import mock_numpy as np
from pytz import timezone

MIN_VALID_HOUR = 7
MAX_VALID_HOUR = 21


def day_week(d=date.today()):
    # retorna el dia de setmana
    weekdays = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
    return weekdays[d.weekday()]


def week_start_date(d=date.today()):
    # Tornem el dilluns d'aquesta setmana
    return d - timedelta(d.weekday())


def get_trimester(completed):
    month = completed.month
    if month >= 9:
        return 1
    elif month <= 3:
        return 2
    else:  # Month from 4 to 8
        return 3


def append_warning(configuration, code):
    warning = models.Warnings.retrieve(code)
    if warning:
        if warning not in configuration.warnings:
            configuration.warnings.append(warning)
    else:
        print "Warning not found: {warning} for older: {older}".format(warning=code, older=configuration.older.id)


def get_order(element):
    if element.order:
        return int(element.order)
    else:
        return 0


def get_sort(element):
    if element.sort:
        return int(element.sort)
    else:
        return 0


def get_filtered_times(session):
    n = 1.5
    sorted_activities = sorted(session.list_activities, key=get_sort)
    last = sorted_activities[-1]
    replaced = 0
    words_minute = last.words_minute
    if last.times and len(last.times) > 0:
        list_times = map(lambda e: int(e), last.times.split(','))
        avg = np.mean(list_times)
        dev = np.std(list_times)
        i = 0
        while i < len(list_times):
            value = list_times[i]
            if abs(value - avg) > n * dev:
                replaced += 1
                list_times.remove(value)
            else:
                i += 1
        words_minute = 60/np.mean(list_times)*1000

    return replaced, words_minute


def get_percentile(older, session):
    """
    Get the percentile for an older
    :param older:
    :param session:
    :return:
    """
    completed = session.completed_time
    trimester = get_trimester(completed)
    course = older.get_course(session.completed_time)
    if course is not None:
        def filter_callback(e):
            #print "c: {0} vs {1} trimester: {2} vs {3}".format(e.course, get_course(session.completed_time).id, e.semester, trimester)
            return e.course == course.id and int(e.semester) == trimester

        list_percentiles = filter(
            filter_callback,
            DataManager.sharedManager().retrieve_all('percentile'))
        type_percentile = session.model_based.type_percentile
        for percentile in list_percentiles:
            if percentile.type == type_percentile:
                _, times = get_filtered_times(session)
                return percentile.get_value(times)
        return None
    else:
        raise models.CourseNotFoundException()


def get_average_data(older, sessions_made, list_used_sessions):
    """
    Get the average data used to check the conditions
    :param older:
    :param sessions_made:
    :param list_used_sessions:
    :return:
    """
    sessions_data = filter(lambda s: s.model_based in list_used_sessions, sessions_made)
    count_percentile = 0
    count_motivation = 0
    ac_percentile = 0
    ac_motivation = 0
    for session in sessions_data:
        percentile = get_percentile(older, session)
        if percentile is not None:
            ac_percentile += percentile
            count_percentile += 1
        count_motivation += 1
        ac_motivation += int(session.status_end)
    if count_percentile > 0:
        return float(ac_percentile) / count_percentile, float(ac_motivation) / count_motivation
    else:
        return None, None


def jump(configuration, jump_config):
    """
    Change the configuration using a jump (BlockJumpCondition or BlockJumpDefault)
    :param configuration:
    :param jump_config:
    :return:
    """
    configuration.lastBlock = configuration.block
    configuration.lastLevel = configuration.level
    if not jump_config.repeatBlock:
        blocks = sorted(configuration.pattern.blocks, key=lambda e: int(e.order))
        index = blocks.index(configuration.block) + 1
        if index < len(blocks):
            configuration.block = blocks[index]
        else:
            print "Next block no existent"
    configuration.level = jump_config.nextLevel
    list_sessions = filter(lambda e: e.level == configuration.level, configuration.block.sessions)
    list_sessions = sorted(list_sessions, key=lambda e: int(e.order))
    configuration.session = list_sessions[0]
    if jump_config.warning is not None:
        configuration.warnings.append(jump_config.warning)


def update_config(configuration, list_sessions_made, list_use_data):
    """
    Update the configuration with the new session to launch
    :param configuration:
    :param list_sessions_made: List of sessions made by the older
    :param list_use_data: List of sessions that was required the information to check the block jump
    :return: If we jump to another level/block or we continue on the same.
    """
    # print configuration.session, list_sessions
    # print configuration.session.id, map(lambda e: e.id, list_sessions)
    current_level = int(configuration.level)
    list_block_sessions = configuration.get_current_block_session()
    list_block_sessions = sorted(list_block_sessions, key=lambda s: int(s.order))
    position = list_block_sessions.index(configuration.session) + 1
    if position < len(list_block_sessions):
        configuration.session = list_block_sessions[position]
    else:
        jump_block = configuration.block.blockJump
        if jump_block is not None:
            try:
                avg_percentile, avg_motivation = get_average_data(configuration.older, list_sessions_made, list_use_data)
                if avg_percentile is not None:
                    conditions = filter(lambda e: int(e.level) == current_level, jump_block.conditions)
                    for condition in conditions:
                        if condition.check(avg_percentile, avg_motivation):
                            jump(configuration, condition)
                            return True
            except models.CourseNotFoundException:
                append_warning(configuration, "P-1.6")

            defaults = filter(lambda e: int(e.level) == current_level, jump_block.defaults)
            if len(defaults) == 1:
                jump(configuration, defaults[0])
                return True

        append_warning(configuration, "P-1.2")
        configuration.session = list_block_sessions[0]
    return False


def pauta(configuration):
    """
    Create a new session using the current configuration
    :param configuration:
    :return:
    """
    model_session = configuration.session
    new_session = models.Session()
    new_session.student = configuration.older
    new_session.publish_date = datetime.today()
    new_session.model_based = model_session.session

    return new_session


def get_counters(sessions, list_sessions, monday):
    not_done_list = filter(lambda e: e.completed_time is None, sessions)  # sessions no fetes
    not_done = len(not_done_list)
    sessions_block = filter(lambda e: e.model_based in list_sessions, not_done_list)
    not_done_pattern = len(sessions_block)
    sessions_week = filter(lambda e: e.model_based in list_sessions,
                           filter(lambda e: e.publish_date and e.publish_date >= monday,
                                  sessions))
    s_week = len(sessions_week)

    return not_done, not_done_pattern, s_week


def generate_lists(configuration, sessions):
    """

    :param configuration:
    :type configuration: OlderConfig
    :param sessions:
    :return: (List of sessions in current block and old block, list of sessions made with current models, list of sessions to use data)
    """
    list_block_sessions = configuration.get_list_block_session()
    # list_block_sessions = sorted(list_block_sessions, key=attrgetter('order'))
    list_sessions = map(lambda e: e.session, list_block_sessions)  # llistat id_sessions del bloc

    sessions_made = filter(lambda e: e.completed_time is not None and e.status_begin is not None,
                           filter(lambda e: e.model_based in list_sessions, sessions))
    sessions_use_data = map(lambda e: e.session, filter(lambda e: e.use_data, configuration.get_current_block_session()))

    return list_sessions, sessions_made, sessions_use_data


def check_warnings(configuration, all_sessions, sessions_made):
    begin_end_limit = -3
    # p = 0.5
    pc = 30
    dif = 5
    europe = timezone("Europe/Madrid")

    if len(sessions_made) > 0:
        sessions_made = sorted(sessions_made, key=lambda e: e.completed_time, reverse=True)
        mot_begin = map(lambda e: int(e.status_begin), sessions_made[0:4])
        mot_begin_end = map(lambda e: int(e.status_end) - int(e.status_begin), sessions_made[0:4])
        avg_mot_begin = np.mean(mot_begin)
        avg_mot_begin_end = np.mean(mot_begin_end)
        last_session = sessions_made[0]

        all_sessions_count = len(all_sessions)
        all_sessions = filter(lambda e: e.publish_date is not None, all_sessions)
        if len(all_sessions) != all_sessions_count:
            append_warning(configuration, "P-1.5")

        all_sessions = sorted(all_sessions, key=lambda e: e.publish_date, reverse=True)
        if len(all_sessions) >= configuration.numberSessions:
            last_sessions = all_sessions[:configuration.numberSessions]
            not_done_sessions = filter(lambda e: e.completed_time is None, last_sessions)
            if len(not_done_sessions) == configuration.numberSessions:
                append_warning(configuration, "S-1.1")

        if avg_mot_begin <= 4:
            append_warning(configuration, "MOT-1.1")
        elif len(mot_begin) >= 2 and mot_begin[1] < 5 and mot_begin[0] < 5:
            append_warning(configuration, "MOT-1.4")
        elif mot_begin[0] < 5:
            append_warning(configuration, "MOT-1.3")
        elif avg_mot_begin <= 6:
            append_warning(configuration, "MOT-1.2")
        """
        else:  # Motiv[0]>=5
            vmax = max(mot_begin)
            vmin = min(mot_begin)
            if mot_begin[0] < mot_begin[1] and vmax - vmin > p:
                append_warning(configuration, "MOT-2.1")
        """

        if avg_mot_begin_end < begin_end_limit:
            append_warning(configuration, "MOT-3.1")
        elif mot_begin_end[0] < begin_end_limit:
            append_warning(configuration, "MOT-3.2")
        elif mot_begin_end[0] < 0:
            append_warning(configuration, "MOT-3.3")

        replaced, _ = get_filtered_times(last_session)

        if replaced > 2 and mot_begin_end[0] < begin_end_limit:
            append_warning(configuration, "CL-1.1")
        elif replaced > 2:
            append_warning(configuration, "CL-1.2")
        elif replaced > 0:
            append_warning(configuration, "CL-1.3")

        try:
            percentile = get_percentile(configuration.older, last_session)
            if percentile < pc and last_session.difficulty < dif:
                append_warning(configuration, "CL-2.1")
        except models.CourseNotFoundException:
            append_warning(configuration, "P-1.6")

        check_time = last_session.completed_time.astimezone(europe).time()
        min_hour = time(MIN_VALID_HOUR, tzinfo=europe)
        max_hour = time(MAX_VALID_HOUR, tzinfo=europe)
        if check_time < min_hour or check_time > max_hour:
            append_warning(configuration, "H-1.1")

    else:
        append_warning(configuration, "P-1.3")


def run(configuration, monday):
    history = models.PatternHistory()
    sessions = models.Session.get(query="student={older}&count=20".format(older=configuration.older.id))

    list_sessions, sessions_made, sessions_use_data = generate_lists(configuration, sessions)

    not_done, not_done_pattern, s_week = get_counters(sessions, list_sessions, monday)
    count = int(configuration.numberSessions)

    check_warnings(configuration, filter(lambda e: e.model_based in list_sessions, sessions), sessions_made)

    if configuration.maxSessionWeek is not None:
        count = min(int(configuration.maxSessionWeek) - s_week, configuration.numberSessions)

    history.sessions = []

    while (not_done_pattern < 2 * configuration.numberSessions and
                   not_done < 10 and count > 0):
        session = pauta(configuration)
        hasJump = update_config(configuration, sessions_made, sessions_use_data)
        if hasJump:
            list_sessions, sessions_made, sessions_use_data = generate_lists(configuration,
                                                                             sessions)
        session.save()

        history.sessions.append(session)

        not_done_pattern += 1
        not_done += 1
        count -= 1

    if not_done == 10:
        append_warning(configuration, "P-1.4")

    history.older = configuration.older
    history.pattern = configuration.pattern
    history.day = datetime.today()
    history.block = configuration.block
    history.level = configuration.level
    history.warnings = configuration.warnings
    history.save()


def main(today=date.today()):
    today_name = day_week(today)  # guardem el nom del dia actual
    llista_configurations = models.OlderConfig.get()  # Llista tots els olders disponibles
    monday = week_start_date(today)
    monday = datetime.combine(monday, datetime.min.time())

    for configuration in llista_configurations:
        working = configuration.workingDays
        if getattr(working, today_name):
            configuration.warnings = []
            try:
                run(configuration, monday)
            except Exception, e:
                print "older: {older} config: {pk}".format(older=configuration.raw("older"), pk=configuration.id)
                append_warning(configuration, "P-1.1")
                print e
                type_, value_, traceback_ = sys.exc_info()
                print "".join(traceback.format_exception(type_, value_, traceback_))
            configuration.save()

def load_cache():
    """
    Load the most part of frecuently used data from the server to don't need to acces
    :return:
    """
    models.Course.get_all()
    models.Percentile.get()
    models.Warnings.get()

if __name__ == "__main__":
    load_cache()
    # Run the program
    main()
