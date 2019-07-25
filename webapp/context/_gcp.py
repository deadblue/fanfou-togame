# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import google.auth
import googleapiclient.discovery
import google.cloud.logging
import google.cloud.tasks

def init():
    # get project_id and location_id
    credentials, project_id = google.auth.default()
    admin_service = googleapiclient.discovery.build(
        serviceName='appengine', version='v1',
        credentials=credentials, cache_discovery=False
    )
    info = admin_service.apps().get(appsId=project_id).execute()
    location_id = info['locationId']

    # config logging
    logging_client = google.cloud.logging.Client(
        credentials=credentials
    )
    logging_client.setup_logging()

    # init cloud-tasks client
    tasks_client = google.cloud.tasks.CloudTasksClient(credentials=credentials)

    return project_id, location_id, tasks_client
