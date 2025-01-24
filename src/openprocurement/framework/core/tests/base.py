import os.path
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import SESSION
from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.tests.base import BaseWebTest as BaseApiWebTest
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.core.utils import calculate_framework_full_date
from openprocurement.tender.core.tests.base import BaseWebTest

here = os.path.dirname(os.path.abspath(__file__))
srequest = SESSION.request

now = get_now()

test_framework_data = {
    "id": "117e88a375404c3faf85cdef60f47902",
    "title": "Узагальнена назва закупівлі",
    "description": "Назва предмета закупівлі",
}

test_framework_item_data = {
    "description": "футляри до державних нагород",
    "classification": {"scheme": "ДК021", "description": "Mustard seeds", "id": "03111600-8"},
    "additionalClassifications": [
        {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ],
    "unit": {
        "name": "кг",
        "code": "KGM",
        "value": {"amount": 6},
    },
    "quantity": 5,
    "deliveryDate": {
        "startDate": (now + timedelta(days=2)).isoformat(),
        "endDate": (now + timedelta(days=5)).isoformat(),
    },
    "deliveryAddress": {
        "countryName": "Україна",
        "postalCode": "79000",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова 1",
    },
}


class BaseFrameworkTest(BaseApiWebTest):
    relative_to = os.path.dirname(__file__)


class FrameworkActionsTestMixin:

    def get_auth(self, role=None):
        if role:
            return ("Basic", (role, ""))
        return self.app.authorization

    def get_framework(self, role=None):
        with change_auth(self.app, self.get_auth(role)):
            url = "/frameworks/{}".format(self.framework_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def create_framework(self, data=None, config=None):
        data = data if data is not None else deepcopy(self.initial_data)
        config = config if config is not None else deepcopy(self.initial_config)

        response = self.app.post_json(
            "/frameworks",
            {
                "data": data,
                "config": config,
            },
        )
        self.framework_token = response.json["access"]["token"]
        self.framework_id = response.json["data"]["id"]
        self.assertEqual(response.json["data"]["frameworkType"], self.framework_type)
        return response

    def activate_framework(self):
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(self.framework_id, self.framework_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["frameworkType"], self.framework_type)
        return response

    def get_submission(self, role=None):
        with change_auth(self.app, self.get_auth(role)):
            url = "/submissions/{}".format(self.submission_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["submissionType"], self.framework_type)
        return response

    def create_submission(self, data=None, config=None, status=201):
        data = data if data is not None else deepcopy(self.initial_submission_data)
        config = config if config is not None else deepcopy(self.initial_submission_config)
        data["frameworkID"] = self.framework_id
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": config,
            },
            status=status,
        )
        if status == 201:
            self.submission_id = response.json["data"]["id"]
            self.submission_token = response.json["access"]["token"]
            self.assertEqual(response.json["data"]["submissionType"], self.framework_type)
        return response

    def activate_submission(self):
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["submissionType"], self.framework_type)
        self.qualification_id = response.json["data"]["qualificationID"]
        return response

    def activate_qualification(self, qualification_id=None):
        qual_id = qualification_id or self.qualification_id
        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(qual_id, self.framework_token),
            {
                "data": {
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/pkcs7-signature",
                    "documentType": "evaluationReports",
                }
            },
        )
        self.assertEqual(response.status, "201 Created")
        response = self.app.patch_json(
            f"/qualifications/{qual_id}?acc_token={self.framework_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["qualificationType"], self.framework_type)
        return response

    def get_agreement(self, role=None):
        with change_auth(self.app, self.get_auth(role)):
            url = "/agreements/{}".format(self.agreement_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["agreementType"], self.framework_type)
        return response


class BaseFrameworkCoreWebTest(BaseWebTest, FrameworkActionsTestMixin):
    initial_data = None
    initial_status = None

    framework_id = None

    periods = None
    now = None
    framework_class = None

    def tearDown(self):
        self.delete_framework()
        super().tearDown()

    def set_status(self, status, extra=None):
        self.now = get_now()
        self.framework_document = self.mongodb.frameworks.get(self.framework_id)
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
                    self.framework_document_patch[period][date] = (
                        self.calculate_period_date(date, period, startend, status)
                    ).isoformat()

    def calculate_period_date(self, date, period, startend, status):
        framework = self.framework_class(self.framework_document)
        period_date_item = self.periods[status][startend][period][date]
        return calculate_framework_full_date(
            self.now,
            period_date_item,
            framework=framework,
            working_days=False,
        )

    def save_changes(self):
        if self.framework_document_patch:
            patch = apply_data_patch(self.framework_document, self.framework_document_patch)
            self.framework_document.update(patch)
            self.mongodb.frameworks.save(self.framework_document)
            self.framework_document = self.mongodb.frameworks.get(self.framework_id)
            self.framework_document_patch = {}

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
            db = self.mongodb.frameworks
            db.delete(self.framework_id)


class BaseAgreementTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
