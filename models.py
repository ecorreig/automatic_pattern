__author__ = 'dracks'

from Api import EndpointProperties
from Api.Manager import DataManager
from Api.EndpointModel import Model
from datetime import datetime


class CourseNotFoundException(Exception):
    pass


@DataManager.endpoint
class Language(Model):
    _name = ['language', 'languages']
    _fields = ['id', 'name']


@DataManager.endpoint
class Older(Model):
    _name = ['student', 'students']
    _fields = ['id', 'birthday', 'group', 'course_difference']
    group = EndpointProperties.BelongsTo('group')
    birthday = EndpointProperties.DateProperty()

    def get_course(self, date=datetime.today()):
        """

        :param date:
        :return: A course instance
        """
        if self.birthday is not None:
            age = date.year - self.birthday.year
            if date.month < 8:
                age -= 1

            for course in DataManager.sharedManager().retrieve_all('course'):
                if int(course.age) == age:
                    return course
            return self.group.course
        else:
            # Thats not good, we don't use the date.
            return self.group.course


@DataManager.endpoint
class Group(Model):
    _name = ['group', 'groups']
    _fields = ['id', 'course', 'name']
    # No es necessari el curs, perque amb l'id en tenim suficient
    course = EndpointProperties.BelongsTo('course')


@DataManager.endpoint
class Course(Model):
    _name = ['course', 'courses']
    _fields = ['id', 'age']


@DataManager.endpoint
class Percentile(Model):
    _name = ['percentile', 'percentiles']
    _fields = ["id", "type", "course", "p0", "p5", "p10", "p15", "p20", "p25", "p30", "p35", "p40", "p45", "p50",
               "p55", "p60", "p65", "p70", "p75", "p80", "p85", "p90", "p95", "p100", "semester"]

    def get_value(self, velocity):
        if velocity < float(getattr(self, "p0")):
            return 0

        for i in range(0, 20):
            percentile = i * 5
            check = (float(getattr(self, "p" + str(percentile))) + float(getattr(self, "p" + str(percentile + 5)))) / 2
            # console.log(percentile+" check : "+ this.get("p"+percentile)+ " vs " + velocity)
            if check >= velocity:
                # console.log(velocity+" -> "+this.get("p"+percentile)+"-"+this.get("p"+(percentile+5)));
                return percentile

        return 105


@DataManager.endpoint
class AttachmentCategories(Model):
    _name = ['attachmentCategory', 'attachmentCategories']
    _fields = ['id', 'name']


@DataManager.endpoint
class Attachment(Model):
    _name = ['attachment', 'attachments']
    _fields = ['id', 'category', 'name', 'description']
    category = EndpointProperties.BelongsTo('attachmentCategory')


@DataManager.endpoint
class Pattern(Model):
    _name = ['pattern', 'patterns']
    _fields = ['id', 'name', 'language', 'blocks']
    language = EndpointProperties.BelongsTo('language')
    blocks = EndpointProperties.HasMany('block')


@DataManager.endpoint
class OlderConfig(Model):
    _name = ['olderPatternRelation', 'olderPatternRelations']
    _fields = ['id', 'older', 'pattern', 'workingDays', 'numberSessions', 'maxSessionWeek', 'block', 'level', 'session',
               'lastBlock', 'lastLevel', 'warnings']
    older = EndpointProperties.BelongsTo('student')
    pattern = EndpointProperties.BelongsTo('pattern')
    workingDays = EndpointProperties.BelongsTo('daysWork')
    session = EndpointProperties.BelongsTo('blockSession')
    block = EndpointProperties.BelongsTo('block')
    warnings = EndpointProperties.HasMany('warning')
    lastBlock = EndpointProperties.BelongsTo('block')

    def get_list_block_session(self):
        blocks_session = self.get_current_block_session()
        if self.lastBlock:
            blocks_session.extend(filter(lambda e: e.level == self.lastLevel, self.lastBlock.sessions))
        return blocks_session

    def get_current_block_session(self):
        current_level = int(self.level)
        return filter(lambda e: int(e.level) == current_level, self.block.sessions)


@DataManager.endpoint
class WorkingDays(Model):
    _name = ['daysWork', 'daysWorks']
    _fields = ['id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    monday = EndpointProperties.BooleanProperty()
    tuesday = EndpointProperties.BooleanProperty()
    wednesday = EndpointProperties.BooleanProperty()
    thursday = EndpointProperties.BooleanProperty()
    friday = EndpointProperties.BooleanProperty()
    saturday = EndpointProperties.BooleanProperty()
    sunday = EndpointProperties.BooleanProperty()


@DataManager.endpoint
class ModelSession(Model):
    _name = ['sessionModel', 'sessionModels']
    _fields = ['id', 'name', 'type_percentile']


@DataManager.endpoint
class Session(Model):
    _name = ['session', 'sessions']
    _fields = ['id', 'student', 'name', 'time', 'completed_time', 'creation_time', 'status_begin', 'status_end',
               'publish_date', 'difficulty', 'tag', 'version', 'model_based', 'list_activities']
    list_activities = EndpointProperties.HasMany('activity')
    completed_time = EndpointProperties.DateProperty()
    publish_date = EndpointProperties.DateProperty()
    model_based = EndpointProperties.BelongsTo('sessionModel')
    student = EndpointProperties.BelongsTo('student')


@DataManager.endpoint
class Activity(Model):
    _name = ['activity', 'activities']
    _fields = ['id', 'sort', 'times', 'words_minute']


@DataManager.endpoint
class Block(Model):
    _name = ['block', 'blocks']
    _fields = ['id', 'name', 'sessions', 'blockJump', 'order']
    sessions = EndpointProperties.HasMany('blockSession')
    blockJump = EndpointProperties.BelongsTo('blockJump')


@DataManager.endpoint
class BlockJump(Model):
    _name = ['blockJump', 'blockJumps']
    _fields = ['id', 'name', 'conditions', 'defaults']
    conditions = EndpointProperties.HasMany('blockJumpCondition')
    defaults = EndpointProperties.HasMany('blockJumpDefault')


@DataManager.endpoint
class BlockJumpCondition(Model):
    _name = ['blockJumpCondition', 'blockJumpConditions']
    _fields = ['id', 'level', 'minPercentile', 'maxPercentile', 'motivation', 'repeatBlock',
               'nextLevel', 'warning']

    repeatBlock = EndpointProperties.BooleanProperty()
    warning = EndpointProperties.BelongsTo('warning')

    def check(self, percentile, motivation):
        # print "{0} < {1} < {2}".format(self.minPercentile, percentile, self.maxPercentile)
        if self.minPercentile is not None and percentile < int(self.minPercentile):
            return False
        if self.maxPercentile is not None and percentile >= int(self.maxPercentile):
            return False
        # TODO Check the motivation
        return True


@DataManager.endpoint
class BlockJumpDefault(Model):
    _name = ['blockJumpDefault', 'blockJumpDefaults']
    _fields = ['id', 'block_jump', 'level', 'repeatBlock', 'nextLevel', 'warning']

    repeatBlock = EndpointProperties.BooleanProperty()
    warning = EndpointProperties.BelongsTo('warning')


@DataManager.endpoint
class BlockSession(Model):
    _name = ['blockSession', 'blockSessions']
    _fields = ['id', 'level', 'order', 'use_data', 'session']
    session = EndpointProperties.BelongsTo('sessionModel')


@DataManager.endpoint
class Warnings(Model):
    _name = ['warning', 'warnings']
    _fields = ['id', 'code', 'level', 'name']

    @classmethod
    def retrieve(cls, code):
        list_warnings = cls._manager.retrieve_all('warning')
        for warning in list_warnings:
            if warning.code == code:
                return warning
        #print "Warning not found - {code}".format(code=code)
        return None


@DataManager.endpoint
class PatternHistory(Model):
    _name = ['patternHistory', 'patternHistories']
    _fields = ["id", "older", "pattern", "day", "block", "level", "description", 'sessions', 'warnings']

    older = EndpointProperties.BelongsTo('student')
    pattern = EndpointProperties.BelongsTo('pattern')
    day = EndpointProperties.DateProperty()
    block = EndpointProperties.BelongsTo('block')
    sessions = EndpointProperties.HasMany('session')
    warnings = EndpointProperties.HasMany('warning')
