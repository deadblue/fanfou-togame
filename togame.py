# -*- coding: utf-8 -*-
'''
Created on 2014/06/26

@author: deadblue
'''

from __future__ import unicode_literals
import binascii
import random
import re

class IllegalProblemException(Exception):
    pass

def deal_status(customer, problem):
    p = re.compile(ur'^(@咎儿 )?(.+?)[?？](.+)?(@咎儿)?$')
    m = p.match(unicode(problem))
    if m is None:
        raise IllegalProblemException()
    if m.group(1) is None and m.group(4) is None:
        raise IllegalProblemException()
    # 拆分问题和选项
    question = m.group(2)
    options = _get_options(m.group(3), question)
    return _deal_problem(customer, question, options)

def deal_message(customer, problem):
    p = re.compile(ur'^(.+?)[?？](.+)?$')
    m = p.match(unicode(problem))
    if m is None:
        raise IllegalProblemException()
    # 提取问题和选项
    question = m.group(1)
    options = _get_options(m.group(2), question)
    return _deal_problem(customer, question, options)

def _get_options(options, question):
    opts = []
    if options is not None:
        # 按分号拆分
        p = re.compile(u'[;；]{1}')
        # 去除重复选项
        opts = set(p.split(options))
        # 过滤空白选项
        opts = filter(lambda x:len(x.strip())!=0, opts)
    if options is None or len(opts) == 0:
        # 不存在选项，从问题中查找选项
        p = re.compile(ur'(.+)([不没]\1)')
        m = p.search(question)
        if m is None:
            raise IllegalProblemException()
        else:
            opts = [m.group(1), m.group(2)]
    return opts

def _deal_problem(customer, question, options):
    result = {
              'question' : question,
              'options' : []
              }
    # 计算各选项的权重，并计算总权重
    total_weight = 0
    for option in options:
        if len(option.strip()) == 0: continue
        # 计算权重，并保证为正数
        base = '%s|%s|%s' % (customer, question, option)
        weight = binascii.crc32(base.encode('utf-8')) & 0xffffffff
        result['options'].append({
                                  'text' : option,
                                  'weight' : weight
                                  })
        total_weight += weight
    if total_weight == 0: raise IllegalProblemException()
    # 按权重降序排序
    result['options'] = sorted(result['options'], key=lambda x:x['weight'], reverse=True)
    # 为每个选项计算一个1~10000的分数，并保证总和为10000
    score_fix = 10000
    for option in result['options']:
        option['score'] = option['weight'] * 10000 / total_weight
        score_fix -= option['score']
    if score_fix != 0:
        result['options'][-1]['score'] += score_fix
    return result

_KAOMOJI = [
            u'o(*≧▽≦)ツ',
            u'(σ≧ω≦)σ',
            u'(っ◕ヮ◕)っ',
            u'(*￣︶￣)つ',
            u'( ´ ▽ ` )ﾉ',
            u'(/▽＼)'
            ]
def kaomoji():
    index = random.randint(0, len(_KAOMOJI) -1)
    return _KAOMOJI[index]