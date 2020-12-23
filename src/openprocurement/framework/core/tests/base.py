# -*- coding: utf-8 -*-
import os.path

from uuid import uuid4
from urllib import urlencode
from base64 import b64encode
from requests import Response

from openprocurement.api.tests.base import BaseWebTest as BaseApiWebTest, change_auth
from openprocurement.api.utils import get_now, apply_data_patch, SESSION
from openprocurement.framework.electroniccatalogue.utils import calculate_framework_date

here = os.path.dirname(os.path.abspath(__file__))
srequest = SESSION.request

test_framework_data = {
    u"id": u"117e88a375404c3faf85cdef60f47902",
    u"title": u"Узагальнена назва закупівлі",
    u"description": u"Назва предмета закупівлі",
}


class BaseFrameworkTest(BaseApiWebTest):
    relative_to = os.path.dirname(__file__)
    docservice = False


class BaseWebTest(BaseApiWebTest):
    initial_auth = ("Basic", ("token", ""))
    docservice = False
    docservice_url = "http://localhost"
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(BaseWebTest, self).setUp()
        if self.docservice:
            self.setUpDS()

    def setUpDS(self):
        self.app.app.registry.docservice_url = self.docservice_url
        test = self

        def request(method, url, **kwargs):
            response = Response()
            if method == "POST" and "/upload" in url:
                url = test.generate_docservice_url()
                response.status_code = 200
                response.encoding = "application/json"
                data = '{{"url":"{url}","hash":"md5:{md5}","format":"{format}","title":"{title}"}}'.format(
                    url=url, md5="0" * 32, title="name.doc", format="application/msword"
                )
                response._content = '{{"data": {data},"get_url":"{url}"}}'.format(url=url, data=data)
                response.reason = "200 OK"
            return response

        SESSION.request = request

    def generate_docservice_url(self):
        uuid = uuid4().hex
        key = self.app.app.registry.docservice_key
        keyid = key.hex_vk()[:8]
        signature = b64encode(key.signature("{}\0{}".format(uuid, "0" * 32)))
        query = {"Signature": signature, "KeyID": keyid}
        return "{}/get/{}?{}".format(self.docservice_url, uuid, urlencode(query))

    def tearDownDS(self):
        SESSION.request = srequest
        self.app.app.registry.docservice_url = None

    def tearDown(self):
        if self.docservice:
            self.tearDownDS()
        super(BaseWebTest, self).tearDown()


class BaseCoreWebTest(BaseWebTest):
    initial_data = None
    initial_status = None
    docservice = False

    framework_id = None

    periods = None
    now = None
    framework_class = None

    def tearDown(self):
        self.delete_framework()
        super(BaseCoreWebTest, self).tearDown()

    def set_status(self, status, extra=None):
        self.now = get_now()
        self.framework_document = self.db.get(self.framework_id)
        self.framework_document_patch = {"status": status}
        self.update_periods(status)
        if extra:
            self.framework_document_patch.update(extra)
        self.save_changes()
        return self.get_framework("chronograph")

    def update_periods(self, status, startend="start"):
        if status in self.periods:
            for period in self.periods[status][startend]:
                self.framework_document_patch.update({period: {}})
                for date in self.periods[status][startend][period]:
                    self.framework_document_patch[period][date] = (self.calculate_period_date(
                        date, period, startend, status
                    )).isoformat()

    def calculate_period_date(self, date, period, startend, status):
        framework = self.framework_class(self.framework_document)
        period_date_item = self.periods[status][startend][period][date]
        return calculate_framework_date(
            self.now, period_date_item, framework=framework, working_days=False
        )

    def save_changes(self):
        if self.framework_document_patch:
            patch = apply_data_patch(self.framework_document, self.framework_document_patch)
            self.framework_document.update(patch)
            self.db.save(self.framework_document)
            self.framework_document = self.db.get(self.framework_id)
            self.framework_document_patch = {}

    def get_framework(self, role):
        with change_auth(self.app, ("Basic", (role, ""))):
            url = "/frameworks/{}".format(self.framework_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def check_chronograph(self, data=None):
        with change_auth(self.app, ("Basic", ("chronograph", ""))):
            url = "/frameworks/{}".format(self.framework_id)
            data = data or {"data": {"id": self.framework_id}}
            response = self.app.patch_json(url, data)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def delete_framework(self):
        if self.framework_id:
            self.db.delete(self.db[self.framework_id])
