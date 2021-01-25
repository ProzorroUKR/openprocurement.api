# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta
from freezegun import freeze_time

import standards

from openprocurement.api.tests.base import BaseWebTest, change_auth
from openprocurement.api.utils import get_now, apply_data_patch, parse_date
from openprocurement.framework.core.tests.base import BaseCoreWebTest
from openprocurement.framework.electroniccatalogue.models import ElectronicCatalogueFramework
from openprocurement.framework.electroniccatalogue.tests.periods import PERIODS


def get_cpb_ids_by_activity():
    """
    Get first active: True and first active: False cpb from standards
    To test rule that only CPB that have "active": true in standards can create electronicCatalogue framework
    https://prozorroukr.github.io/standards/organizations/authorized_cpb.json

    :return: active cpb id, non active cpb id
    """
    active_cpb = []
    non_active_cpb = []
    authorized_cpb = standards.load("organizations/authorized_cpb.json")
    for cpb in authorized_cpb:
        if not active_cpb or not non_active_cpb:
            id_ = cpb["identifier"]["id"]
            active_cpb.append(id_) if cpb["active"] else non_active_cpb.append(id_)
    return active_cpb[0], non_active_cpb[0]


active_cpb_id, non_active_cpb_id = get_cpb_ids_by_activity()

now = get_now()
test_electronicCatalogue_data = {
    "procuringEntity": {
        "contactPoint": {
            "telephone": u"0440000000",
            "name": u"Назва організації(ЦЗО)",
            "email": u"aa@aa.com"
        },
        "identifier": {
            "scheme": u"UA-EDR",
            "id": active_cpb_id,
            "legalName": u"Назва організації(ЦЗО)"
        },
        "kind": u"central",
        "address": {
            "countryName": u"Україна",
            "postalCode": u"01220",
            "region": u"м. Київ",
            "streetAddress": u"вул. Банкова, 11, корпус 1",
            "locality": u"м. Київ"
        },
        "name": u"Повна назва юридичної організації."
    },
    "additionalClassifications": [
        {
            "scheme": u"ДК003",
            "id": u"17.21.1",
            "description": u"папір і картон гофровані, паперова й картонна тара"
        }
    ],
    "classification": {
        "scheme": u"ДК021",
        "description": u"Mustard seeds",
        "id": u"03111600-8"
    },
    "title": u"Узагальнена назва закупівлі",
    "description": u"Назва предмета закупівлі",
    "qualificationPeriod": {"endDate": (now + timedelta(days=60)).isoformat()}
}

test_electronicCatalogue_documents = [
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "framework.doc",
        "format": "application/msword",
        "datePublished": "2020-09-08T01:00:00+03:00",
        "id": "cd52b90af77e4f5b8cb0f210e83987b5",
        "dateModified": "2020-09-08T01:00:00+03:00"
    },
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "framework_additional_docs.doc",
        "format": "application/msword",
        "datePublished": "2020-09-08T01:00:00+03:00",
        "id": "3fe9486c38a1473ca201e42ebbf9b648",
        "dateModified": "2020-09-08T01:00:00+03:00"
    },
    {
        "hash": "md5:00000000000000000000000000000000",
        "title": "framework_additional_docs.doc",
        "format": "application/msword",
        "datePublished": "2020-09-08T01:00:00+03:00",
        "id": "3fe9486c38a1473ca201e42ebbf9b648",
        "dateModified": "2020-09-08T01:00:00+03:00"
    }
]

tenderer = {
    "name": "Державне управління справами",
    "name_en": "State administration",
    "identifier": {
        "legalName_en": "dus.gov.ua",
        "legalName": "Державне управління справами",
        "scheme": "UA-EDR",
        "id": "00037256",
        "uri": "http://www.dus.gov.ua/"
    },
    "address": {
        "countryName": "Україна",
        "postalCode": "01220",
        "region": "м. Київ",
        "locality": "м. Київ",
        "streetAddress": "вул. Банкова, 11, корпус 1"
    },
    "contactPoint": {
        "name": "Державне управління справами",
        "name_en": "State administration",
        "telephone": "0440000000"
    },
    "scale": "micro"
}

test_submission_data = {
    "tenderers": [tenderer],
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))


class BaseElectronicCatalogueWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_electronicCatalogue_data
    framework_class = ElectronicCatalogueFramework
    docservice = False
    periods = PERIODS

    def create_framework(self):
        data = deepcopy(self.initial_data)

        response = self.app.post_json("/frameworks", {"data": data})
        self.framework_document = response.json["data"]
        self.framework_token = response.json["access"]["token"]
        self.framework_id = response.json["data"]["id"]


class ElectronicCatalogueContentWebTest(BaseElectronicCatalogueWebTest):
    initial_status = None

    def setUp(self):
        super(ElectronicCatalogueContentWebTest, self).setUp()
        self.create_framework()


class BaseDSElectronicCatalogueContentWebTest(ElectronicCatalogueContentWebTest):
    docservice = True


class BaseSubmissionContentWebTest(ElectronicCatalogueContentWebTest):
    initial_submission_data = None

    def get_submission(self, role):
        with change_auth(self.app, ("Basic", (role, ""))):
            url = "/submissions/{}".format(self.submission_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def set_submission_status(self, status, extra=None):
        self.now = get_now()
        self.submission_document = self.db.get(self.submission_id)
        self.submission_document_patch = {"status": status}
        if extra:
            self.submission_document_patch.update(extra)
        self.save_submission_changes()
        return self.get_submission("chronograph")

    def save_submission_changes(self):
        if self.submission_document_patch:
            patch = apply_data_patch(self.submission_document, self.submission_document_patch)
            self.submission_document.update(patch)
            self.db.save(self.submission_document)
            self.submission_document = self.db.get(self.submission_id)
            self.submission_document_patch = {}

    def create_submission(self):
        response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
        self.submission_id = response.json["data"]["id"]
        self.submission_token = response.json["access"]["token"]

    def setUp(self):
        super(BaseSubmissionContentWebTest, self).setUp()
        self.initial_submission_data["frameworkID"] = self.framework_id
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(self.framework_id, self.framework_token),
            {"data": {"status": "active"}}
        )
        submission_date = parse_date(response.json["data"]["enquiryPeriod"]["endDate"])

        self.freezer = freeze_time((submission_date + timedelta(hours=1)).isoformat(), tick=True)
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()


class SubmissionContentWebTest(BaseSubmissionContentWebTest):
    def setUp(self):
        super(SubmissionContentWebTest, self).setUp()
        self.create_submission()
