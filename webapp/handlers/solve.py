# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import logging

import flask

from webapp import context, http_status
import fanfou
import togame
import kaomoji

_logger = logging.getLogger(__name__)

class ReplyException(Exception):
    
    def __init__(self):
        super(ReplyException, self).__init__(self)


def handler():
    req_id = flask.request.values.get('request_id')
    if req_id is None:
        return '', http_status.BAD_REQUEST

    req = context.db.get_request(request_id=req_id)
    if req is None:
        return 'Request has been solved', http_status.ALREADY_DONE

    quest = togame.parse(req)
    if quest is None:
        # invalid request, remove it and return
        context.db.remove_request(req_id)
        return 'Ignored', http_status.IGNORED

    try:
        answer = togame.solve(quest)
        if 'status' == req['source_type']:
            reply = '@%s 结果发表%s %s' % (
                req['user_name'], kaomoji.one(), str(answer)
            )
            # post status
            result = context.fanfou_client.status_update(
                status=reply, in_reply_to_status_id=req['source_id']
            )
            has_error, error_message = fanfou.is_error_result(result)
            if has_error:
                _logger.error('Reply status failed: %s', error_message)
        elif 'message' == req['source_type']:
            reply = '结果发表%s %s' % (
                kaomoji.one(), str(answer)
            )
            # send message
            result = context.fanfou_client.direct_message_new(
                user=req['user_id'], text=reply,
                in_reply_to_id=req['source_id']
            )
            has_error, error_message = fanfou.is_error_result(result)
            if has_error:
                _logger.error('Send message failed: %s', error_message)
            else:
                # delete message
                context.fanfou_client.direct_message_destroy(req['source_id'])
                context.fanfou_client.direct_message_destroy(result['id'])
        # remove request from DB
        context.db.remove_request(req_id)
    except ReplyException:
        return 'Retry for reply failed', http_status.INTERNAL_SERVER_ERROR

    return 'Solved', http_status.OK
