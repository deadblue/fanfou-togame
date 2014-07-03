# -*- coding: utf-8 -*-
'''
Created on 2014/06/25

@author: deadblue
'''

from __future__ import unicode_literals
from google.appengine.api import taskqueue
import api
import datetime
import logging
import model
import togame
import webapp2

class FetchHandler(webapp2.RequestHandler):
    def get(self):
        client = api.FanfouClient()
        # get notification info
        ntf = client.account_notification()
        if ntf['mentions'] > 0:
            self._fetch_status_problem(client, ntf['mentions'])
        if ntf['direct_messages'] > 0:
            self._fetch_message_problem(client, ntf['direct_messages'])
    def _fetch_status_problem(self, client, count):
        '''
        获取来自提醒的问题，存入数据库并创建处理任务
        '''
        # fetch mentions from fanfou
        pc = model.ProblemCursor.get_by_key_name('status')
        last_status_id = pc.last_id if pc is not None else None
        statuses = client.status_mentions(last_status_id, count)
        for status in reversed(statuses):
            # save to datastore
            last_status_id = status['id']
            sp = model.StatusProblem(key_name=status['id'])
            sp.status_id = status['id']
            sp.text = status['text']
            sp.user_id = status['user']['id']
            sp.user_name = status['user']['name']
            sp.fetch_time = datetime.datetime.now()
            sp.state = 0
            sp.save()
            # create deal task
            retry_opts = taskqueue.TaskRetryOptions(task_retry_limit=10)
            taskqueue.add(queue_name='togame', retry_options=retry_opts,
                          url='/deal_status', method='GET',
                          params={'status_id' : status['id']})
        # update last status id
        if last_status_id is not None:
            if pc is None:
                pc = model.ProblemCursor(key_name='status')
            pc.last_id = last_status_id
            pc.save()
    def _fetch_message_problem(self, client, count):
        '''
        获取来自私信的问题，存入数据库并创建处理任务
        '''
        # fetch message from fanfou
        pc = model.ProblemCursor.get_by_key_name('message')
        last_message_id = pc.last_id if pc is not None else None
        messages = client.message_inbox(last_message_id, count)
        for message in reversed(messages):
            # save to datastore
            last_message_id = message['id']
            mp = model.MessageProblem(key_name=message['id'])
            mp.message_id = message['id']
            mp.text = message['text']
            mp.user_id = message['sender']['id']
            mp.user_name = message['sender']['name']
            mp.state = 0
            mp.save()
            # create deal task
            retry_opts = taskqueue.TaskRetryOptions(task_retry_limit=10)
            taskqueue.add(queue_name='togame', retry_options=retry_opts,
                          url='/deal_message', method='GET',
                          params={'message_id' : message['id']})
        # update last message id
        if last_message_id is not None:
            if pc is None:
                pc = model.ProblemCursor(key_name='message')
            pc.last_id = last_message_id
            pc.save()

class DealStatusHandler(webapp2.RequestHandler):
    def get(self):
        status_id = self.request.get('status_id')
        if status_id is None:
            return
        sp = model.StatusProblem.get_by_key_name(status_id)
        if sp is None:
            logging.warn('No such status: %s' % status_id)
            return
        try:
            # deal problem
            result = togame.deal_status(sp.user_name, sp.text)
            answer = '@%s 结果发表%s %s' % (sp.user_name, togame.kaomoji(), _join_options(result['options']))
            # send to fanfou
            client = api.FanfouClient()
            client.status_update(answer, sp.status_id, sp.user_id)
            sp.state = 2    # means resolved
        except togame.IllegalProblemException:
            sp.state = 3    # means illegal
            logging.warn('Illegal problem!')
        finally:
            sp.save()

class DealMessageHandler(webapp2.RequestHandler):
    def get(self):
        message_id = self.request.get('message_id')
        if message_id is None:
            return
        mp = model.MessageProblem.get_by_key_name(message_id)
        if mp is None:
            logging.warn('No such message: %d', message_id)
            return
        try:
            # deal problem
            result = togame.deal_message(mp.user_name, mp.text)
            answer = '结果发表%s %s' % (togame.kaomoji(), _join_options(result['options']))
            # send message and delete it
            client = api.FanfouClient()
            message = client.message_new(mp.user_id, answer, mp.message_id)
            client.message_destory(mp.message_id)
            client.message_destory(message['id'])
        except togame.IllegalProblemException:
            logging.warn('Illegal problem!')
        finally:
            mp.delete()

def _join_options(options):
    buf = []
    for option in options:
        precent = option['score'] / 100.0
        buf.append('%s(%.2f%%)' % (option['text'], precent))
    return '；'.join(buf)
