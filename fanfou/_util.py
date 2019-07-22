# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import time
import random
import hmac
import hashlib
import base64

API_HOST = 'http://api.fanfou.com'
OAUTH_SIGNATURE_METHOD = 'HMAC-SHA1'

# environment names
ENV_API_KEY      = 'FANFOU_API_KEY'
ENV_API_SECRET   = 'FANFOU_API_SECRET'
ENV_OAUTH_TOKEN  = 'FANFOU_OAUTH_TOKEN'
ENV_OAUTH_SECRET = 'FANFOU_OAUTH_SECRET'


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
