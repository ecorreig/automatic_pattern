__author__ = 'dracks'

from Api import EndpointProperties
from Api.Manager import DataManager
from Api.EndpointModel import Model


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
    _fields = ['id', 'older', 'pattern', 'workingDays', 'numberSessions','maxSessionWeek', 'block', 'level', 'session']
    pattern=EndpointProperties.BelongsTo('pattern')
    workingDays=EndpointProperties.BelongsTo('daysWork')
    session=EndpointProperties.BelongsTo('session')
    block = EndpointProperties.BelongsTo('block')

@DataManager.endpoint
class WorkingDays(Model):
    _name = ['daysWork', 'daysWorks']
    _fields = ['id', 'monday', 'tuesday', 'wednesday', 'thursday','friday', 'saturday', 'sunday']


@DataManager.endpoint
class ModelSession(Model):
    _name=['sessionModel', 'sessionModels']
    _fields=['id', 'name']


@DataManager.endpoint
class Session(Model):
    _name = ['session', 'sessions']
    _fields = ['id', 'student', 'name', 'time', 'completed_time','creation_time', 'status_begin', 'status_end', 'publish_date', 'difficulty', 'tag', 'version', 'model_based']


@DataManager.endpoint
class Block(Model):
    _name = ['block', 'blocks']
    _fields = ['id', 'name', 'sessions', 'block_jump_condition', 'order']
    sessions = EndpointProperties.HasMany('blockSession')
    block_jump_condition=EndpointProperties.BelongsTo('blockJumpCondition')


@DataManager.endpoint
class BlockJumpCondition (Model):
    _name = ['blockJumpCondition', 'blockJumpConditions']
    _fields = ['id', 'block_jump', 'current_level', 'min_percentile', 'max_percentile', 'motivation', 'repeat_block', 'next_level', 'warning']


@DataManager.endpoint
class BlockJumpDefault (Model):
    _name = ['blockJumpDefault', 'blockJumpDefaults']
    _fields = ['id', 'block_jump', 'current_level', 'repeat_block', 'next_level', 'warning']


@DataManager.endpoint
class BlockSession(Model):
    _name=['blockSession','blockSessions']
    _fields=['id', 'level','order', 'useData', 'session']
    #sessions=EndpointProperties.BelongsTo('modelSession')


@DataManager.endpoint
class Language(Model):
    _name = ['language', 'languages']
    _fields = ['id', 'name']
