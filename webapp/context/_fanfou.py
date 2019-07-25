# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import os

import fanfou.api

# environment names
ENV_API_KEY      = 'FANFOU_API_KEY'
ENV_API_SECRET   = 'FANFOU_API_SECRET'
ENV_OAUTH_TOKEN  = 'FANFOU_OAUTH_TOKEN'
ENV_OAUTH_SECRET = 'FANFOU_OAUTH_SECRET'

def init():
    api_key = os.environ.get(ENV_API_KEY)
    api_secret = os.environ.get(ENV_API_SECRET)
    oauth_token = os.environ.get(ENV_OAUTH_TOKEN)
    oauth_secret = os.environ.get(ENV_OAUTH_SECRET)

    client = fanfou.api.Client(api_key, api_secret)
    client.oauth_set_token(oauth_token, oauth_secret)
    return client
