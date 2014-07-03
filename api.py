# -*- coding: utf-8 -*-
'''
Created on 2014/06/25

@author: deadblue
'''

import config
import inspect
import json
import logging
import oauthlib
import urllib
import urllib2

# 签名算法
_FANFOU_SIGNATURE_METHOD = 'HMAC-SHA1'
# API根地址
_FANFOU_API_HOST = 'http://api.fanfou.com/'

class OAuthException(Exception):
    pass

def oauth_rpc(url, method='GET'):
    url = '%s%s' % (_FANFOU_API_HOST, url)
    def rpc_invoker_creator(func):
        arg_spec = inspect.getargspec(func)
        arg_names = arg_spec.args
        # 获取参数的默认值定义
        arg_defs = {}
        if arg_spec.defaults:
            for i in xrange(-1, -1 - len(arg_spec.defaults), -1):
                arg_defs[arg_names[i]] = arg_spec.defaults[i]
        def rpc_invoker(*args, **kwargs):
            # 准备调用API的参数
            params = [
                      ('oauth_consumer_key', config.FANFOU_API_KEY),
                      ('oauth_token', config.FANFOU_OAUTH_TOKEN),
                      ('oauth_signature_method', _FANFOU_SIGNATURE_METHOD),
                      ('oauth_timestamp', oauthlib.timestamp()),
                      ('oauth_nonce', oauthlib.nonce()),
                      ]
            # 参数处理
            for i in xrange(1, len(arg_names)):
                arg_name = arg_names[i]
                arg_value = None
                if kwargs is not None and kwargs.has_key(arg_name):
                    arg_value = kwargs[arg_name]
                elif args is not None and i < len(args):
                    arg_value = args[i]
                elif arg_defs.has_key(arg_name):
                    arg_value = arg_defs[arg_name]
                if arg_value is not None:
                    if type(arg_value) is unicode:
                        arg_value = arg_value.encode('utf-8')
                    params.append((arg_name, arg_value))
            # 计算签名
            secert = '%s&%s' % (config.FANFOU_API_SECERT, config.FANFOU_OAUTH_TOKEN_SECERT)
            signature = oauthlib.signature(method, url, params, secert)
            params.append(('oauth_signature', signature))
            # 发起http请求
            data = urllib.urlencode(params)
            if method == 'POST':
                req = urllib2.Request(url, data)
            else:
                req = urllib2.Request('%s?%s' % (url, data))
            req.add_header('Authorization', 'OAuth')
            try:
                resp = urllib2.urlopen(req)
                return json.load(resp)
            except urllib2.HTTPError as he:
                if he.code == 401:
                    logging.warn('OAuth error: %s' % he.read())
                raise OAuthException()
        return rpc_invoker
    return rpc_invoker_creator


class FanfouClient():

    def get_authorize_url(self):
        '''
        获取认证URL
        '''
        url = 'http://fanfou.com/oauth/request_token'
        params = [
                  ('oauth_consumer_key', config.FANFOU_API_KEY),
                  ('oauth_signature_method', _FANFOU_SIGNATURE_METHOD),
                  ('oauth_timestamp', oauthlib.timestamp()),
                  ('oauth_nonce', oauthlib.nonce())
                  ]
        secert = '%s&' % config.FANFOU_API_SECERT
        params.append(('oauth_signature', oauthlib.signature('GET', url, params, secert)))
        url = '%s?%s' % (url, urllib.urlencode(params))
        resp = urllib2.urlopen(url)
        # 读取结果
        result = resp.read()
        # 拆分token和secert
        token, secert = result.split('&')
        token = token[12:]
        secert = secert[19:]
        auth_url = 'http://fanfou.com/oauth/authorize?oauth_token=%s&oauth_callback=oob' % token
        return {
                'token' : token,
                'secert' : secert,
                'url' : auth_url
                }
    def get_access_token(self, token, secert, pin):
        '''
        获取访问令牌和密钥
        '''
        url = 'http://fanfou.com/oauth/access_token'
        params = [
                  ('oauth_consumer_key', config.FANFOU_API_KEY),
                  ('oauth_token', token),
                  ('oauth_signature_method', _FANFOU_SIGNATURE_METHOD),
                  ('oauth_verifier', pin),
                  ('oauth_timestamp', oauthlib.timestamp()),
                  ('oauth_nonce', oauthlib.nonce())
                  ]
        secert = '%s&%s' % (config.FANFOU_API_SECERT, secert)
        params.append(('oauth_signature', oauthlib.signature('GET', url, params, secert)))
        url = '%s?%s' % (url, urllib.urlencode(params))
        resp = urllib2.urlopen(url)
        result = resp.read()
        token, secert = result.split('&')
        return {
                'token' : token[12:],
                'secert' : secert[19:]
                }

    @oauth_rpc('account/notification.json')
    def account_notification(self):
        pass

    @oauth_rpc('followers/ids.json')
    def followers_ids(self):
        pass

    @oauth_rpc('users/followers.json')
    def users_followers(self, count=20, page=None, mode='lite'):
        pass
    @oauth_rpc('users/show.json')
    def users_show(self, id, mode='lite'):  # @ReservedAssignment
        pass

    @oauth_rpc('statuses/user_timeline.json')
    def status_user_timeline(self, count=20):
        pass
    @oauth_rpc('statuses/mentions.json')
    def status_mentions(self, since_id=None, count=20, mode='lite'):
        pass
    @oauth_rpc('statuses/update.json', 'POST')
    def status_update(self, status, in_reply_to_status_id=None, in_reply_to_user_id=None):
        pass
    
    @oauth_rpc('direct_messages/inbox.json')
    def message_inbox(self, since_id=None, count=20, mode='lite'):
        pass
    @oauth_rpc('direct_messages/new.json', 'POST')
    def message_new(self, user, text, in_reply_to_id=None, mode='lite'):
        pass
    @oauth_rpc('direct_messages/destroy.json', 'POST')
    def message_destory(self, id):  # @ReservedAssignment
        pass
