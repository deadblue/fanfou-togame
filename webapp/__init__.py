# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import flask

from webapp.handlers import fetch, solve

def create_app():
    app = flask.Flask(__name__)

    app.add_url_rule(
        rule='/fetch', endpoint='handler_fetch', view_func=fetch.handler
    )
    app.add_url_rule(
        rule='/solve', endpoint='handler_solve', view_func=solve.handler
    )

    return app