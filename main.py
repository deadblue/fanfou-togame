# -*- coding: utf-8 -*-

__author__ = 'deadblue'

# init context at first
import webapp.context

import webapp
app = webapp.create_app()

__all__ = ['app']
