# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import flask

from webapp import context
import togame
import kaomoji

def handler():
    req_id = flask.request.values.get('request_id')
    if req_id is None:
        return 'Nothing to do.', 200
    req = context.db.take_request(request_id=req_id, delete=True)
    if req is None:
        return 'No such request.', 200

    quest = togame.parse(req)
    if quest is None:
        return 'Invalid request.', 200
    answer = togame.solve(quest)

    if 'status' == req['source_type']:
        reply = '@%s 结果发表%s %s' % (
            req['user_name'], kaomoji.one(), str(answer)
        )
        # post status
        context.fanfou_client.status_update(
            status=reply, in_reply_to_status_id=req['source_id']
        )
    elif 'message' == req['source_type']:
        reply = '结果发表%s %s' % (
            kaomoji.one(), str(answer)
        )
        # send message
        result = context.fanfou_client.direct_message_new(
            user=req['user_id'], text=reply,
            in_reply_to_id=req['source_id']
        )
        # delete message
        context.fanfou_client.direct_message_destroy(req['source_id'])
        context.fanfou_client.direct_message_destroy(result['id'])

    return '', 200
