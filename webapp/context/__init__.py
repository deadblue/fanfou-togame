# -*- coding: utf-8 -*-

__author__ = 'deadblue'

from webapp.context import _gcp
project_id, location_id, tasks_client = _gcp.init()

from webapp.context import _fanfou
fanfou_client = _fanfou.init()

from webapp.context import _db
db = _db.init()

import logging
logging.info('Webapp context initialized!')

__all__ = ['project_id', 'location_id', 'tasks_client', 'fanfou_client', 'db']
