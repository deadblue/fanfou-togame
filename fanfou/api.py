# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import inspect
import logging
import sys
import traceback
import urllib.parse

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
            'timeout': (3.0, 10.0)
        }
        if 'GET' == method:
            request_kwargs['params'] = params
        else:
            request_kwargs['data'] = params
        # send request
        retry, result = True, None
        while retry:
            try:
                with self._agent.request(method, url, **request_kwargs) as resp:
                    if 200 <= resp.status_code < 500:
                        result = resp.json()
                        retry = False
                    else:
                        _logger.warning('Unexpected API response: %s', resp.text)
            except requests.ConnectionError:
                _logger.error('Retry calling API for network error!')
            except requests.Timeout:
                _logger.error('Retry calling API for request timeount!')
            except Exception as ue:
                _logger.error('Unexpected error: %r', ue)
                retry = False
        return result

    def _calculate_signature(self, method, url, params):
        # sort params
        sorted_params = sorted(params.items(), key=lambda p:p[0])
        # build basestring
        query_string = urllib.parse.urlencode(sorted_params, quote_via=urllib.parse.quote)
        base_string = '&'.join([
            method, urllib.parse.quote(url, safe=''),
            urllib.parse.quote(query_string, safe='')
        ])
        _logger.debug('basestring => [%s]', base_string)
        sign_secret = '%s&' % self._api_secret
        if self._oauth_secret is not None:
            sign_secret += self._oauth_secret
        return util.signature(sign_secret, base_string)

    def oauth_authorize_request(self):
        # request token for authorizing
        params = {
            'oauth_consumer_key': self._api_key,
            'oauth_signature_method': util.OAUTH_SIGNATURE_METHOD,
            'oauth_timestamp': util.timestamp(),
            'oauth_nonce': util.nonce()
        }
        params['oauth_signature'] = self._calculate_signature('GET', util.API_REQUEST_TOKEN, params)
        with self._agent.get(util.API_REQUEST_TOKEN, params=params) as resp:
            result = urllib.parse.parse_qsl(resp.text)
            for name, value in result:
                if 'oauth_token' == name:
                    self._oauth_token = value
                elif 'oauth_token_secret' == name:
                    self._oauth_secret = value
        # build authorize url
        qs = urllib.parse.urlencode({
            'oauth_token': self._oauth_token,
            'oauth_callback': 'oob'
        }, quote_via=urllib.parse.quote)
        return '%s?%s' % (
            util.API_AUTHORIZE, qs
        )

    def oauth_authorize(self, verify_code):
        params = {
            'oauth_consumer_key': self._api_key,
            'oauth_token': self._oauth_token,
            'oauth_verifier': verify_code,
            'oauth_signature_method': util.OAUTH_SIGNATURE_METHOD,
            'oauth_timestamp': util.timestamp(),
            'oauth_nonce': util.nonce()
        }
        params['oauth_signature'] = self._calculate_signature('POST', util.API_ACCESS_TOKEN, params)
        with self._agent.post(util.API_ACCESS_TOKEN, data=params) as resp:
            result = urllib.parse.parse_qsl(resp.text)
            for name, value in result:
                if 'oauth_token' == name:
                    self._oauth_token = value
                elif 'oauth_token_secret' == name:
                    self._oauth_secret = value
        return self._oauth_token, self._oauth_secret

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
