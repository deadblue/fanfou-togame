# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import re

_MENTION_PATTERN = re.compile('^@.+?\s+(.+?)[?？](.*)$')
_MESSAGE_PATTERN = re.compile('^(.+?)[?？](.*)$')
_OPTION_SEPARATOR_PATTERN = re.compile('[;；]')

class Quest(object):

    _user_name, _create_time, _question, _options = None, None, None, None

    def __init__(self, user_name, create_time, question, options):
        self._user_name = user_name
        self._create_time = create_time
        self._question = question
        self._options = options

    @property
    def question(self):
        return self._question

    @property
    def options(self):
        return self._options

    @property
    def user_name(self):
        return self._user_name

    @property
    def create_time(self):
        return self._create_time


def parse(request):
    """
    :param request:
    :return:
    :rtype: Quest
    """
    if request is not None and 'source_type' in request:
        if request['source_type'] == 'status':
            return _parse_mention_status(request)
        elif request['source_type'] == 'message':
            return _parse_direct_message(request)
    return None

def _parse_mention_status(request):
    # check format
    m = _MENTION_PATTERN.match(request['text'])
    if m is None:
        return None
    # parse
    question = m.group(1)
    options = _split_options(m.group(2))
    return Quest(request['user_name'], request['create_time'], question, options)

def _parse_direct_message(request):
    # check format
    m = _MESSAGE_PATTERN.match(request['text'])
    if m is None:
        return None
    # parse
    question = m.group(1)
    options = _split_options(m.group(2))
    return Quest(request['user_name'], request['create_time'], question, options)

def _split_options(options_text):
    opts = []
    for opt in _OPTION_SEPARATOR_PATTERN.split(options_text):
        opt = opt.strip()
        if len(opt) > 0:
            opts.append(opt)
    # If user just asked a question,
    # use 是(yes) and 否(no) as the options.
    if len(opts) == 0:
        opts = ['是', '否']
    return opts
