# -*- coding: utf-8 -*-
import os

import webtest
import unittest

from types import FunctionType

from paste.deploy import loadapp

from openprocurement.api.constants import VERSION
from openprocurement.api.design import sync_design


wsgiapp = None


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
    return FunctionType(func.func_code, func.func_globals,
                        'test_' + func.func_name, closure=func.func_closure)


class PrefixedTestRequest(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseTestApp(webtest.TestApp):
    RequestClass = PrefixedTestRequest

    def reset(self):
        super(BaseTestApp, self).reset()
        if self.app.registry.db.name in self.app.registry.couchdb_server:
            self.app.registry.couchdb_server.delete(self.app.registry.db.name)
        self.app.registry.db = self.app.registry.couchdb_server.create(self.app.registry.db.name)
        sync_design(self.app.registry.db)


class BaseWebTest(unittest.TestCase):
    """
    Base Web Test to test openprocurement.api.
    It setups the database before each test and delete it after.
    """
    AppClass = BaseTestApp

    relative_uri = "config:tests.ini"
    relative_to = os.path.dirname(__file__)

    initial_auth = None

    @classmethod
    def setUpClass(cls):
        global wsgiapp
        wsgiapp = wsgiapp or loadapp(cls.relative_uri, relative_to=cls.relative_to)
        cls.app = cls.AppClass(wsgiapp)
        cls.couchdb_server = cls.app.app.registry.couchdb_server
        cls.db = cls.app.app.registry.db

    def setUp(self):
        self.app.authorization = self.initial_auth
        self.app.reset()
