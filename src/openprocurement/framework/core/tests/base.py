# -*- coding: utf-8 -*-
import os.path

from openprocurement.api.tests.base import BaseWebTest as BaseApiWebTest, change_auth
from openprocurement.api.utils import get_now, apply_data_patch, SESSION
from openprocurement.framework.electroniccatalogue.utils import calculate_framework_date
from openprocurement.tender.core.tests.base import BaseWebTest

here = os.path.dirname(os.path.abspath(__file__))
srequest = SESSION.request

test_framework_data = {
    "id": "117e88a375404c3faf85cdef60f47902",
    "title": "Узагальнена назва закупівлі",
    "description": "Назва предмета закупівлі",
}


class BaseFrameworkTest(BaseApiWebTest):
    relative_to = os.path.dirname(__file__)
    docservice = False
    database_keys = ("frameworks", "submissions", "qualifications", "agreements")


class BaseCoreWebTest(BaseWebTest):
    initial_data = None
    initial_status = None
    docservice = False
    database_keys = ("frameworks", "submissions", "qualifications", "agreements")

    framework_id = None

    periods = None
    now = None
    framework_class = None

    def tearDown(self):
        self.delete_framework()
        super(BaseCoreWebTest, self).tearDown()

    def set_status(self, status, extra=None):
        self.now = get_now()
        self.framework_document = self.databases.frameworks.get(self.framework_id)
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
            self.now, period_date_item, framework, working_days=False
        )

    def save_changes(self):
        if self.framework_document_patch:
            patch = apply_data_patch(self.framework_document, self.framework_document_patch)
            self.framework_document.update(patch)
            self.databases.frameworks.save(self.framework_document)
            self.framework_document = self.databases.frameworks.get(self.framework_id)
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
            db = self.databases.frameworks
            db.delete(db[self.framework_id])


class BaseAgreementTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    docservice = False
    database_keys = ("frameworks", "submissions", "qualifications", "agreements")
