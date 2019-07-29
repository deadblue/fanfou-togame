# -*- coding: utf-8 -*-

__author__ = 'deadblue'

import datetime
import logging
import os
import atexit

import pymongo
import bson.objectid

ENV_MONGO_URI = 'MONGO_URI'
ENV_FANFOU_ACCOUNT = 'FANFOU_ACCOUNT'

COLLECTION_BOOKMARK = 'bookmark'
COLLECTION_REQUEST = 'request'

_logger = logging.getLogger(__name__)

class DB:

    _bookmark_account = None

    _client = None
    _db = None

    def __init__(self):
        # get account for bookmark
        self._bookmark_account = os.environ.get(ENV_FANFOU_ACCOUNT)
        # connect to mongodb
        mongo_uri = os.environ.get(ENV_MONGO_URI)
        _logger.debug('Mongo URI: %s', mongo_uri)
        self._client = pymongo.MongoClient(host=mongo_uri)
        self._db = self._client.get_database()


    def get_bookmark(self):
        """
        Get bookmark from DB.

        :return:
        """
        bookmark = {
            'status_id': None,
            'message_id': None
        }
        coll = self._db.get_collection(COLLECTION_BOOKMARK)
        cursor = coll.find_one(filter={
            'account': self._bookmark_account
        })
        if cursor is not None:
            bookmark.update({
                'status_id': cursor['status_id'],
                'message_id': cursor['message_id']
            })
        return bookmark

    def update_bookmark(self, status_id, message_id):
        """
        Update bookmark.

        :param status_id:
        :param message_id:
        :return:
        """
        doc = {}
        if status_id is not None:
            doc['status_id'] = status_id
        if message_id is not None:
            doc['message_id'] = message_id

        # search exists bookmark
        coll = self._db.get_collection(COLLECTION_BOOKMARK)
        cursor = coll.find_one(filter={
            'account': self._bookmark_account
        })
        if cursor is None:
            doc['account'] = self._bookmark_account
            doc['create_time'] = datetime.datetime.now()
            coll.insert(doc)
        else:
            doc['update_time'] = datetime.datetime.now()
            coll.update_one(filter={
                '_id': cursor['_id'],
            }, update={
                '$set': doc
            })

    def store_requests(self, requests):
        """
        Store requests into DB, return the DB id.
        :return:
        """
        coll = self._db.get_collection(COLLECTION_REQUEST)
        result = coll.insert_many(requests)
        return result.inserted_ids

    def get_request(self, request_id):
        """
        Get request from DB.
        :param request_id: request ID
        :return:
        """
        doc_id = bson.objectid.ObjectId(request_id)
        coll = self._db.get_collection(COLLECTION_REQUEST)
        doc = coll.find_one(filter={
            '_id': doc_id
        })
        return doc

    def remove_request(self, request_id):
        """
        Delete request from DB.
        :param request_id: request ID
        :return:
        """
        doc_id = bson.objectid.ObjectId(request_id)
        coll = self._db.get_collection(COLLECTION_REQUEST)
        coll.delete_one({
            '_id': doc_id
        })

    def release(self):
        _logger.info('Closing mongo connections ...')
        self._client.close()

def init():
    db = DB()
    atexit.register(db.release)
    return db
