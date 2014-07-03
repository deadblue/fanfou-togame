# -*- coding: utf-8 -*-
'''
Created on 2014/06/25

@author: deadblue
'''

from google.appengine.ext import db

class StatusProblem(db.Model):
    status_id = db.StringProperty()
    text = db.StringProperty()
    user_id = db.StringProperty()
    user_name = db.StringProperty()
    fetch_time = db.DateTimeProperty()
    state = db.IntegerProperty()

class MessageProblem(db.Model):
    message_id = db.StringProperty()
    text = db.StringProperty()
    user_id = db.StringProperty()
    user_name = db.StringProperty()
    state = db.IntegerProperty()

class ProblemCursor(db.Model):
    last_id = db.StringProperty()
