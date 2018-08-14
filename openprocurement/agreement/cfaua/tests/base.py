# -*- coding: utf-8 -*-
import os
import os.path
import json
import unittest
import webtest
from base64 import b64encode
from copy import deepcopy
from datetime import datetime
from requests.models import Response
from urllib import urlencode
from uuid import uuid4
from openprocurement.api.constants import VERSION, SESSION
from openprocurement.api.utils import get_now


here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, 'data/agreement.json')) as _in:
    TEST_AGREEMENT = json.load(_in)


with open(os.path.join(here, 'data/documents.json')) as _in:
    TEST_DOCUMENTS = json.load(_in)



now = datetime.now()

test_agreement_data = deepcopy(TEST_AGREEMENT)


test_agreement_data_wo_items = deepcopy(test_agreement_data)
del test_agreement_data_wo_items['items']


documents = deepcopy(TEST_DOCUMENTS)


class PrefixedRequestClass(webtest.app.TestRequest):

    @classmethod
    def blank(cls, path, *args, **kwargs):
        path = '/api/%s%s' % (VERSION, path)
        return webtest.app.TestRequest.blank(path, *args, **kwargs)


class BaseWebTest(unittest.TestCase):
    """Base Web Test to test openprocurement.agreement.cfaua.

    It setups the database before each test and delete it after.
    """
    initial_auth = ('Basic', ('token', ''))
    docservice = False

    def setUp(self):
        self.app = webtest.TestApp(
            "config:tests.ini", relative_to=os.path.dirname(__file__))
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


class BaseAgreementWebTest(BaseWebTest):
    initial_data = test_agreement_data

    def setUp(self):
        super(BaseAgreementWebTest, self).setUp()
        self.create_agreement()

    def create_agreement(self):
        data = deepcopy(self.initial_data)

        orig_auth = self.app.authorization
        self.app.authorization = ('Basic', ('agreements', ''))
        response = self.app.post_json('/agreements', {'data': data})
        self.agreement = response.json['data']
        # self.agreement_token = response.json['access']['token']
        self.agreement_id = self.agreement['id']
        self.app.authorization = orig_auth

    def tearDown(self):
        del self.db[self.agreement_id]
        super(BaseAgreementWebTest, self).tearDown()


class BaseAgreementContentWebTest(BaseAgreementWebTest):

    def setUp(self):
        super(BaseAgreementContentWebTest, self).setUp()
        response = self.app.patch_json('/agreements/{}/credentials?acc_token={}'.format(
            self.agreement_id, self.initial_data['tender_token']), {'data': {}})
        self.agreement_token = response.json['access']['token']
