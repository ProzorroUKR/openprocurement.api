import json
import uuid
import os.path
import unittest
import webtest
from base64 import b64encode
from copy import deepcopy
from contextlib import contextmanager
from uuid import uuid4
from urllib import urlencode
from openprocurement.api.constants import SESSION
from openprocurement.api.utils import get_now
from requests.models import Response

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
    docservice = False

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini",
            relative_to=self.relative_to
        )
        self.app.RequestClass = PrefixedRequestClass
        self.app.authorization = self.initial_auth
        self.couchdb_server = self.app.app.registry.couchdb_server
        self.db = self.app.app.registry.db
        if self.docservice:
            self.setUpDS()

    def setUpDS(self):
        self.app.app.registry.docservice_url = 'http://localhost'
        test = self
        def request(method, url, **kwargs):
            response = Response()
            if method == 'POST' and '/upload' in url:
                url = test.generate_docservice_url()
                response.status_code = 200
                response.encoding = 'application/json'
                response._content = '{{"data":{{"url":"{url}","hash":"md5:{md5}","format":"application/msword","title":"name.doc"}},"get_url":"{url}"}}'.format(url=url, md5='0'*32)
                response.reason = '200 OK'
            return response

        self._srequest = SESSION.request
        SESSION.request = request

    def generate_docservice_url(self):
        uuid = uuid4().hex
        key = self.app.app.registry.docservice_key
        keyid = key.hex_vk()[:8]
        signature = b64encode(key.signature("{}\0{}".format(uuid, '0' * 32)))
        query = {'Signature': signature, 'KeyID': keyid}
        return "http://localhost/get/{}?{}".format(uuid, urlencode(query))

    def tearDownDS(self):
        SESSION.request = self._srequest

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        del self.couchdb_server[self.db.name]


class BaseAgreementWebTest(BaseAgreementTest):
    initial_data = TEST_AGREEMENT

    def setUp(self):
        super(BaseAgreementWebTest, self).setUp()
        self.create_agreement()

    def tearDown(self):
        if self.agreement_id:
            del self.db[self.agreement_id]
        super(BaseAgreementWebTest, self).tearDown()

    def create_agreement(self):
        data = deepcopy(self.initial_data)
        data['id'] = uuid.uuid4().hex
        with change_auth(self.app, ('Basic', ('agreements', ''))) as app:
            response = self.app.post_json('/agreements', {'data': data})
        agreement = response.json['data']
        self.agreement_token = response.json['access']['token']
        self.agreement_id = agreement['id']


class BaseDSAgreementWebTest(BaseAgreementWebTest):
    docservice = True


@contextmanager
def change_auth(app, auth):
    authorization = app.authorization
    app.authorization = auth
    yield app
    app.authorization = authorization