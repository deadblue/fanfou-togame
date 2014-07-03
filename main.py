# -*- coding: utf-8 -*-
'''
Created on 2014/02/28

@author: deadblue
'''

import handler
import logging
import webapp2

logging.basicConfig(level=logging.DEBUG)
app = webapp2.WSGIApplication([
                               (r'/fetch', handler.FetchHandler),
                               (r'/deal_status', handler.DealStatusHandler),
                               (r'/deal_message', handler.DealMessageHandler),
                               ], debug=False)