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
class Block(Model):
    _name = ['block', 'blocks']
    _fields = ['id', 'name']


@DataManager.endpoint
class Language(Model):
    _name = ['language', 'languages']
    _fields = ['id', 'name']