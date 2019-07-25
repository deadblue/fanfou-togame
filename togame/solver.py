# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import binascii
import datetime

import togame.parser

class Answer(object):

    _options = None

    def __init__(self):
        self._options = []

    def add_option(self, text, score):
        self._options.append({
            'text': text,
            'score': score
        })

    def __str__(self):
        buf = []
        for option in self._options:
            precent = option['score'] / 100.0
            buf.append('%s(%.2f%%)' % (option['text'], precent))
        return '；'.join(buf)


def solve(quest):
    """
    :type quest: togame.parser.Quest
    :param quest:

    :rtype: Answer
    :return:
    """
    # calculate weight and sorted
    options, total_weight = [], 0
    for option in quest.options:
        weight = _calc_weight(
            quest.user_name, quest.question, quest.create_time, option
        )
        options.append({
            'text': option,
            'weight': weight
        })
        total_weight += weight
    options.sort(key=lambda o: o['weight'], reverse=True)
    # calculate socre
    score_fix = 10000
    for option in options:
        option['score'] = int(option['weight'] * 10000 / total_weight)
        score_fix -= option['score']
    if score_fix != 0:
        options[-1]['score'] += score_fix

    answer = Answer()
    for option in options:
        answer.add_option(option['text'], option['score'])
    return answer

def _calc_weight(user_name, question, create_time, option):
    """
    :type user_name: str
    :param user_name:

    :type question: str
    :param question:

    :type create_time: datetime.datetime
    :param create_time:

    :type option: str
    :param option:

    :return:
    """
    text = '%s|%s|%s|%s' % (
        user_name, question, create_time.isoformat(), option
    )
    return binascii.crc32(text.encode('utf-8')) & 0xffffffff
