# -*- coding: utf-8 -*-

__author__ = 'deadblue'

from urllib.parse import quote, urlencode
import inspect
import logging
import os
import sys
import traceback

import requests

from fanfou import _util as util

_logger = logging.getLogger(__name__)

def fanfou_api(path, method='GET'):
    api_url = '%s/%s' % (util.API_HOST, path)
    def invoker_wrapper(func):
        def invoker(client, *args, **kwargs):
            params = {}
            call_args = inspect.getcallargs(func, client, *args, **kwargs)
            for k, v in call_args.items():
                if 'self' == k or v is None: continue
                params[k] = v
            return client.oauth_call_api(method, api_url, params)
        return invoker
    return invoker_wrapper


class Client(object):

    _agent = None

    _api_key = None
    _api_secret = None
    _oauth_token = None
    _oauth_secret = None

    def __init__(self, api_key=None, api_secret=None):
        self._api_key = api_key
        self._api_secret = api_secret
        # setup agent
        agent = requests.Session()
        agent.headers['User-Agent'] = 'FanfouClient/1.0 (python/%d.%d; requests/%s)' % (
            sys.version_info.major, sys.version_info.minor, requests.__version__
        )
        self._agent = agent
        # merge environment variables
        self._merge_environ()

    def _merge_environ(self):
        if self._api_key is None:
            self._api_key = os.environ.get(util.ENV_API_KEY)
        if self._api_secret is None:
            self._api_secret = os.environ.get(util.ENV_API_SECRET)
        self._oauth_token = os.environ.get(util.ENV_OAUTH_TOKEN)
        self._oauth_secret = os.environ.get(util.ENV_OAUTH_SECRET)

    def oauth_set_token(self, token, token_secret):
        self._oauth_token = token
        self._oauth_secret = token_secret

    def oauth_call_api(self, method, url, params=None):
        # append oauth parameters
        if params is None: params = {}
        params.update({
            'oauth_consumer_key': self._api_key,
            'oauth_token': self._oauth_token,
            'oauth_signature_method': util.OAUTH_SIGNATURE_METHOD,
            'oauth_timestamp': util.timestamp(),
            'oauth_nonce': util.nonce()
        })
        params['oauth_signature'] = self._calculate_signature(method, url, params)
        # prepare arguments
        request_kwargs = {
            'headers': {
                'Accept': '*/*',
                'Authorization': 'OAuth'
            },
            'timeout': (10.0, 30.0)
        }
        if 'GET' == method:
            request_kwargs['params'] = params
        else:
            request_kwargs['data'] = params
        # send request
        result = None
        try:
            resp = self._agent.request(method, url, **request_kwargs)
            resp.raise_for_status()
            result = resp.json()
        except:
            _logger.error('Call API failed: %s', traceback.format_exc())
        return result

    def _calculate_signature(self, method, url, params):
        # sort params
        sorted_params = sorted(params.items(), key=lambda p:p[0])
        # build basestring
        querystring = urlencode(sorted_params, quote_via=quote)
        basestring = '&'.join([
            method, quote(url, safe=''),
            quote(querystring, safe='')
        ])
        _logger.debug('basestring => [%s]', basestring)
        sign_secret = '%s&' % self._api_secret
        if self._oauth_secret is not None:
            sign_secret += self._oauth_secret
        return util.signature(sign_secret, basestring)

    @fanfou_api('account/rate_limit_status.json')
    def account_rate_limit_status(self):
        pass

    @fanfou_api('account/verify_credentials.json')
    def account_verify_credentials(self, mode='default'):
        pass

    @fanfou_api('account/notification.json')
    def account_notification(self):
        pass

    @fanfou_api('statuses/mentions.json')
    def status_mentions(self, count=60, since_id=None, mode='lite'):
        pass

    @fanfou_api('statuses/update.json', 'POST')
    def status_update(self, status, in_reply_to_status_id=None, mode='lite'):
        pass

    @fanfou_api('direct_messages/inbox.json')
    def direct_message_inbox(self, count=60, since_id=None, mode='lite'):
        pass

    @fanfou_api('direct_messages/new.json', 'POST')
    def direct_message_new(self, user, text, in_reply_to_id=None, mode='lite'):
        pass

    @fanfou_api('direct_messages/destroy.json', 'POST')
    def direct_message_destroy(self, id):
        pass

