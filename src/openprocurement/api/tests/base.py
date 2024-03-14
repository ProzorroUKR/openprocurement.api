import os
import unittest
from contextlib import contextmanager
from types import FunctionType

import pytest
import webtest
from paste.deploy.loadwsgi import loadapp

from openprocurement.api.constants import TWO_PHASE_COMMIT_FROM, VERSION
from openprocurement.api.utils import get_now

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
        path = "/api/{}{}".format(VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseTestApp(webtest.TestApp):
    RequestClass = PrefixedTestRequest


app_cache = {}


class BaseWebTest(unittest.TestCase):
    """
    Base Web Test to test openprocurement.api.
    It setups the database before each test and delete it after.
    """

    maxDiff = None
    AppClass = BaseTestApp

    relative_uri = "config:tests.ini"
    relative_to = os.path.dirname(__file__)

    initial_auth = None
    mongodb = None

    @classmethod
    def setUpClass(cls):
        key = (cls.relative_uri, cls.relative_to)
        if key not in app_cache:
            app_cache[key] = cls.AppClass(loadwsgiapp(cls.relative_uri, relative_to=cls.relative_to))
        cls.app = app_cache[key]
        # cls.app = cls.AppClass(loadwsgiapp(cls.relative_uri, relative_to=cls.relative_to))

        cls.mongodb = cls.app.app.registry.mongodb
        cls.clean_mongodb()

    def setUp(self):
        self.app.authorization = self.initial_auth

    def tearDown(self):
        self.clean_mongodb()

    @classmethod
    def clean_mongodb(cls):
        for collection in cls.mongodb.collections.keys():
            collection = getattr(cls.mongodb, collection, None)
            if collection:  # plugins are optional
                collection.flush()
        cls.mongodb.flush_sequences()


@pytest.fixture(scope="session")
def singleton_app():
    app = BaseTestApp(loadwsgiapp("config:tests.ini", relative_to=os.path.dirname(__file__)))
    app.app.registry.docservice_url = "http://localhost"
    return app


@pytest.fixture(scope="function")
def app(singleton_app):
    singleton_app.authorization = None
    yield singleton_app
    mongodb = singleton_app.app.registry.mongodb
    if hasattr(mongodb, "tenders"):
        mongodb.tenders.flush()
    if hasattr(mongodb, "plans"):
        mongodb.plans.flush()
    if hasattr(mongodb, "contracts"):
        mongodb.contracts.flush()


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization
