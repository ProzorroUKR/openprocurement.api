import json
import os.path
import unittest
import webtest
from copy import deepcopy
from contextlib import contextmanager
from openprocurement.api.utils import get_now


here = os.path.dirname(os.path.abspath(__file__))
now = get_now()
with open(os.path.join(here, 'data/agreement.json')) as _in:
    TEST_AGREEMENT = json.load(_in)


class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % ('2.4', path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseAgreementTest(unittest.TestCase):
    relative_to = os.path.dirname(__file__)
    initial_auth = ('Basic', ('token', ''))

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini",
            relative_to=self.relative_to
        )
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = self.initial_auth
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db

    def tearDown(self):
        del self.couchdb_server[self.db.name]


class BaseAgreementWebTest(BaseAgreementTest):
    initial_data = TEST_AGREEMENT

    def setUp(self):
        super(BaseAgreementWebTest, self).setUp()
        self.create_agreement()

    def tearDown(self):
        del self.db[self.agreement_id]
        super(BaseAgreementWebTest, self).tearDown()

    def create_agreement(self):
        data = deepcopy(self.initial_data)
        with change_auth(self.app, ('Basic', ('agreements', ''))) as app:
            response = self.app.post_json('/agreements', {'data': data})
        agreement = response.json['data']
        self.agreement_token = response.json['access']['token']
        self.agreement_id = agreement['id']


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization