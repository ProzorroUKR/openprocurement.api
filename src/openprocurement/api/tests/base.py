# -*- coding: utf-8 -*-
from contextlib import contextmanager

from paste.deploy.loadwsgi import loadapp
from types import FunctionType
from openprocurement.api.constants import VERSION
from openprocurement.api.design import sync_design
import webtest
import unittest
import pytest
import os


COUCHBD_NAME_SETTING = "couchdb.db_name"
wsgiapp = None


def loadwsgiapp(uri, **kwargs):
    if os.environ.get("SINGLE_APP", False):
        global wsgiapp
        wsgiapp = wsgiapp or loadapp(uri, **kwargs)
        return wsgiapp
    return loadapp(uri, **kwargs)


def snitch(func):
    """
        This method is used to add test function to TestCase classes.
        snitch method gets test function and returns a copy of this function
        with 'test_' prefix at the beginning (to identify this function as
        an executable test).
        It provides a way to implement a storage (python module that
        contains non-executable test functions) for tests and to include
        different set of functions into different test cases.
    """
    return FunctionType(func.__code__, func.__globals__, "test_" + func.__name__, closure=func.__closure__)


class PrefixedTestRequest(webtest.app.TestRequest):
    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = "/api/%s%s" % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseTestApp(webtest.TestApp):
    RequestClass = PrefixedTestRequest

    def __init__(self, *args, **kwargs):
        super(BaseTestApp, self).__init__(*args, **kwargs)

    def reset(self):
        super(BaseTestApp, self).reset()
        self.recreate_db()

    def recreate_db(self):
        self.drop_db()
        return self.create_db()

    def create_db(self):
        db_name = os.environ.get("DB_NAME", self.app.registry.settings[COUCHBD_NAME_SETTING])
        self.app.registry.db = self.app.registry.couchdb_server.create(db_name)
        sync_design(self.app.registry.db)
        return self.app.registry.db

    def drop_db(self):
        db_name = self.app.registry.db.name
        if db_name and db_name in self.app.registry.couchdb_server:
            self.app.registry.couchdb_server.delete(db_name)

    def get_db(self):
        if self.app.registry.db:
            return self.app.registry.db

    def clean_db(self):
        if self.app.registry.db:
            rows = self.app.registry.db.get("_all_docs", include_docs=True).get("rows", "")
            docs = []
            for row in rows:
                if row['id'].startswith('_'):
                    continue
                doc = row['doc']
                doc['_deleted'] = True
                docs.append(doc)
            self.app.registry.db.update(docs)


class BaseWebTest(unittest.TestCase):
    """
    Base Web Test to test openprocurement.api.
    It setups the database before each test and delete it after.
    """

    AppClass = BaseTestApp

    relative_uri = "config:tests.ini"
    relative_to = os.path.dirname(__file__)

    initial_auth = None

    database_keys = tuple()  # specify database keys that used in a test class
    databases = None

    @classmethod
    def setUpClass(cls):
        cls.app = cls.AppClass(loadwsgiapp(cls.relative_uri, relative_to=cls.relative_to))
        cls.db = cls.app.recreate_db()
        cls.databases = cls.app.app.registry.databases
        if cls.database_keys:   # work with specific databases
            cls.clean_databases()

    def setUp(self):
        self.app.authorization = self.initial_auth

    def tearDown(self):
        self.app.clean_db()
        if self.database_keys:
            self.clean_databases()

    @classmethod
    def clean_databases(cls):
        for db_name in cls.database_keys:
            database = cls.databases[db_name]
            docs = []
            for row in database.get("_all_docs", include_docs=True).get("rows", ""):
                if row['id'].startswith('_'):
                    continue
                doc = row['doc']
                doc['_deleted'] = True
                docs.append(doc)
            database.update(docs)


@pytest.fixture(scope="session")
def singleton_app():
    app = BaseTestApp(loadwsgiapp("config:tests.ini", relative_to=os.path.dirname(__file__)))
    app.app.registry.docservice_url = "http://localhost"
    return app


@pytest.fixture(scope="function")
def app(singleton_app):
    singleton_app.authorization = None
    singleton_app.recreate_db()
    yield singleton_app
    singleton_app.drop_db()


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization
