# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import time
import random
import hmac
import hashlib
import base64

API_HOST = 'http://api.fanfou.com'
OAUTH_SIGNATURE_METHOD = 'HMAC-SHA1'

def timestamp():
    return int(time.time() * 1000)

def nonce():
    return '%x' % random.randint(999999, timestamp())

def signature(secret, message):
    if isinstance(secret, str):
        secret = secret.encode()
    if isinstance(message, str):
        message = message.encode()
    sign = hmac.new(secret, message, hashlib.sha1)
    return base64.b64encode( sign.digest() )
