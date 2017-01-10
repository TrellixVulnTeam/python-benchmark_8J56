from __future__ import unicode_literals

from django.db import models

# Create your models here.

from mongoengine import EmbeddedDocument
from mongoengine import Document
from mongoengine import StringField
from mongoengine import IntField
from mongoengine import DateTimeField
from mongoengine import ListField
from mongoengine import FloatField
from mongoengine import EmbeddedDocumentField


class Choice(EmbeddedDocument):
    choice_text = StringField(max_length=200)
    votes = IntField(default=0)


class Poll(Document):
    question = StringField(max_length=200)
    pub_date = DateTimeField(help_text='date published')
    choices = ListField(EmbeddedDocumentField(Choice))


class Task(Document):
    name = StringField(max_length=200)
    meta = {"collection": "tasks"}



class Server(Document):
    id = IntField()
    # ip = StringField(max_length=32)
    company = StringField(max_length=32)
    # series = StringField(max_length=128)
    # type = StringField(max_length=128)
    # core = IntField()
    # memory = FloatField()
    # data_disk_type = StringField(max_length=128)

    meta = {"collection": "servers"}


