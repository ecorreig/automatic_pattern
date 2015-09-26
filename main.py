__author__ = 'dracks'

import models
from Api.Manager import DataManager
import datetime
from datetime import date, timedelta
from operator import attrgetter


def test():
    es = DataManager.sharedManager().query('language', 'es')
    print es
    print es.name
    print es.id
    patterns = models.Pattern.get()
    print (patterns[0].name)
    len(patterns)
    # print(patterns[0].id)
    # print(patterns[0].language.name)
    print(patterns[0].blocks)

    # print (patterns[-1].id)
    # print (patterns[-1].name)
    # print (patterns[-1].language.name)


#    nou.language = models.Language.get("es")
#    nou.save()

def day_week():
    # retorna el dia de setmana
    weekdays = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
    return weekdays[datetime.datetime.today().weekday()]


def week_start_date(d=datetime.datetime.today()):
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


def get_percentile(older, session):
    """
    Get the percentile for an older
    :param older:
    :param session:
    :return:
    """
    completed = session.completed_time
    trimester = get_trimester(completed)
    get_course = older.get_course

    def filter_callback(e):
        return e.course == get_course(session.completed_time).id and e.semester == trimester

    list_percentiles = filter(
        filter_callback,
        DataManager.sharedManager().retrieve_all('percentiles'))
    type_percentile = session.model_based.type_percentile
    for percentile in list_percentiles:
        if percentile.type == type_percentile:
            sorted_activities = sorted(session.list_activities, key=lambda e: e.order)
            last = sorted_activities[-1]
            return percentile.get_value(last.words_minute)
    return None


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
        ac_motivation += session.status_end
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
    if not jump_config.repeatBlock:
        blocks = sorted(configuration.pattern.blocks, key=lambda e: e.order)
        index = blocks.index(configuration.block) + 1
        if index < len(blocks):
            configuration.block = blocks[index]
        else:
            print "Next block no existent"
    configuration.level = jump_config.nextLevel
    list_sessions = filter(lambda e: e.level == configuration.level, configuration.block.sessions)
    list_sessions = sorted(list_sessions, key=lambda e: e.order)
    configuration.session = list_sessions[0].session
    if jump_config.warning is not None:
        configuration.warnings.append(jump_config.warning)


def update_config(configuration, list_sessions, list_sessions_made, list_use_data):
    """
    Update the configuration with the new session to launch
    :param configuration:
    :param list_sessions:
    :return:
    """
    position = list_sessions.index(configuration.session)
    if position < len(list_sessions):
        configuration.session = list_sessions[position + 1]
    else:
        jump_block = configuration.block.blockJump
        if jump_block is not None:
            current_level = configuration.level
            avg_percentile, avg_motivation = get_average_data(configuration.older, list_sessions_made, list_use_data)
            if avg_percentile is not None:
                conditions = filter(lambda e: e.level == current_level, jump_block.conditions)
                for condition in conditions:
                    if condition.check(avg_percentile, avg_motivation):
                        jump(configuration, condition)

            defaults = filter(lambda e: e.level == current_level, jump_block.defaults)
            if len(defaults) == 1:
                jump(configuration, defaults[0])
        else:
            configuration.session = list_sessions[0]


def pauta(configuration):
    """
    Create a new session using the current configuration
    :param configuration:
    :return:
    """
    model_session = configuration.session
    new_session = models.Session()
    new_session.student = configuration.older
    new_session.publishDate = datetime.datetime.today()
    new_session.modelBased = model_session

    return new_session


def main():
    today = day_week()  # guardem el nom del dia actual
    llista_configurations = models.OlderConfig.get()  # Llista tots els olders disponibles
    monday = week_start_date()

    models.Course.get_all()
    models.Percentile.get_all()

    for configuration in llista_configurations:
        working = configuration.workingDays
        if (getattr(working, today)):
            block = configuration.block
            level = configuration.level
            list_block_sessions = filter(lambda e: e.level == level,
                                         block.sessions)  # llistat de sessions al bloc (amb atributs)
            list_block_sessions = sorted(list_block_sessions, key=attrgetter('order'))
            list_sessions = map(lambda e: e.session, list_block_sessions)  # llistat id_sessions del bloc
            # position=list_sessions.index(session)


            sessions = models.Session.get(query="student={older}&size=20".format(older=configuration.older))
            not_done_list = filter(lambda e: e.completed_time is None, sessions)  # sessions no fetes
            not_done = len(not_done_list)
            sessions_block = filter(lambda e: e.model_based in list_sessions, not_done_list)
            not_done_pattern = len(sessions_block)
            sessions_week = filter(lambda e: e.publish_date >= str(monday), sessions)
            s_week = len(sessions_week)
            cont = configuration.numberSessions

            sessions_made = filter(lambda e: e.completed_time is not None, sessions)
            sessions_use_data = map(lambda e: e.session, filter(lambda e: e.useData, list_block_sessions))

            while (not_done_pattern < 2 * configuration.numberSessions and
                           s_week < configuration.maxSessionWeek and
                           not_done < 10 and cont > 0):
                session = pauta(configuration)
                update_config(configuration, list_sessions, sessions_made, sessions_use_data)
                session.save()

                not_done_pattern += 1
                s_week += 1
                not_done += 1
                cont -= 1


if __name__ == "__main__":
    main()
