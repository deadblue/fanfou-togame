# -*- coding: utf-8 -*-
'''
Created on 2014/06/25

@author: deadblue
'''

import base64
import hashlib
import hmac
import random
import time
import urllib

def get_timestamp():
    return int(time.time())


def get_nonce():
    return '%x' % random.randint(999999, get_timestamp())

def get_signature(method, url, params, secert):
    data = []
    for k,v in params:
        v = urllib.quote(str(v), '~')
        data.append('%s=%s' % (k, v))
    data = urllib.quote('&'.join(sorted(data)), '~')
    base = '%s&%s&%s' % (method, urllib.quote(url, ''), data)
    sign = hmac.new(secert, base, hashlib.sha1)
    return base64.b64encode(sign.digest())


timestamp = get_timestamp
nonce = get_nonce
signature = get_signature