# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import datetime
import logging
import traceback

from google.api_core import retry

from webapp import context

_DATETIME_FORMAT = '%a %b %d %H:%M:%S %z %Y'
_TASK_QUEUE_NAME = 'solve-queue'

_logger = logging.getLogger(__name__)

def handler():
    # fetch mention statuses and direct messages
    bookmark, reqs = context.db.get_bookmark(), []
    last_status_id, last_message_id = None, None
    statuses = context.fanfou_client.status_mentions(since_id=bookmark['status_id'])
    if statuses is not None and len(statuses) > 0:
        last_status_id = statuses[0]['id']
        for status in statuses:
            reqs.append({
                'source_type': 'status',
                'source_id': status['id'],
                'user_id': status['user']['id'],
                'user_name': status['user']['name'],
                'text': status['text'],
                'create_time': datetime.datetime.strptime(status['created_at'], _DATETIME_FORMAT)
            })
    messages = context.fanfou_client.direct_message_inbox(since_id=bookmark['message_id'])
    if messages is not None and len(messages) > 0:
        last_message_id = messages[0]['id']
        for message in messages:
            reqs.append({
                'source_type': 'message',
                'source_id': message['id'],
                'user_id': message['sender']['id'],
                'user_name': message['sender']['name'],
                'text': message['text'],
                'create_time': datetime.datetime.strptime(message['created_at'], _DATETIME_FORMAT)
            })
    if len(reqs) == 0:
        return 'No new request', 200

    # update bookmark
    context.db.update_bookmark(last_status_id, last_message_id)

    # store the requests to DB
    req_ids = context.db.store_requests(reqs)

    # create tasks to solve them
    queue_path, task_count = context.tasks_client.queue_path(
        context.project_id, context.location_id, _TASK_QUEUE_NAME
    ), 0
    for req_id in req_ids:
        try:
            context.tasks_client.create_task(parent=queue_path, task={
                'app_engine_http_request': {
                    'http_method': 'GET',
                    'relative_uri': '/solve?request_id=%s' % str(req_id)
                }
            }, retry=retry.Retry(predicate=retry.if_transient_error))
            task_count += 1
        except:
            _logger.error('Create task failed: %s', traceback.format_exc())
    _logger.info('Create tasks: %d', task_count)
    return 'Create tasks: %d.' % task_count, 200
