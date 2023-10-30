from contextlib import contextmanager
from mock import patch
from datetime import timedelta

from paste.deploy.loadwsgi import loadapp
from types import FunctionType
from openprocurement.api.constants import VERSION, TWO_PHASE_COMMIT_FROM
from openprocurement.api.database import COLLECTION_CLASSES
from openprocurement.api.utils import get_now
import webtest
import unittest
import pytest
import os


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

    def set_initial_status(self, tender, status=None):
        from openprocurement.tender.core.tests.criteria_utils import add_criteria
        add_criteria(self, tender["data"]["id"], tender["access"]["token"])
        response = self.patch_json(
            f"/tenders/{tender['data']['id']}?acc_token={tender['access']['token']}",
            {"data": {"status": status}},
        )
        assert response.status == "200 OK"
        return response


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
        for collection in COLLECTION_CLASSES.keys():
            collection = getattr(cls.mongodb, collection, None)
            if collection:  # plugins are optional
                collection.flush()
        cls.mongodb.flush_sequences()

    def set_initial_status(self, tender, status=None):
        if not status:
            status = self.primary_tender_status
        response = self.app.set_initial_status(tender, status)
        assert response.status == "200 OK"
        return response

    def create_bid(self, tender_id, bid_data, status=None):
        response = self.app.post_json("/tenders/{}/bids".format(tender_id), {"data": bid_data})
        token = response.json["access"]["token"]

        bid = response.json["data"]
        if bid_data.get("status", "") != "draft" and get_now() > TWO_PHASE_COMMIT_FROM:
            response = self.set_responses(tender_id, response.json, status=status)
            if response.json and "data" in response.json:
                bid = response.json["data"]

        return bid, token

    def set_responses(self, tender_id, bid, status=None):
        from openprocurement.tender.core.tests.criteria_utils import generate_responses

        tender = self.mongodb.tenders.get(tender_id)

        if not status:
            status = "pending"

        patch_data = {"status": status}
        if "requirementResponses" not in bid["data"]:
            rr = generate_responses(self, tender_id)
            if rr:
                patch_data["requirementResponses"] = rr

        response = self.app.patch_json(
            f"/tenders/{tender_id}/bids/{bid['data']['id']}?acc_token={bid['access']['token']}",
            {"data": patch_data},
        )
        assert response.status == "200 OK"
        return response


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
