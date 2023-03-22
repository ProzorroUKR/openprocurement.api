# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from datetime import timedelta
from freezegun import freeze_time

from openprocurement.api.tests.base import (
    BaseWebTest,
    change_auth,
)
from openprocurement.api.utils import (
    get_now,
    apply_data_patch,
)
from openprocurement.framework.core.tests.base import BaseCoreWebTest
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.models import (
    Framework,
    Submission,
    Agreement,
)
from openprocurement.framework.dps.tests.periods import PERIODS

now = get_now()
test_framework_dps_data = {
    "frameworkType": DPS_TYPE,
    "procuringEntity": {
        "contactPoint": {
            "name": "Державне управління справами",
            "telephone": "+0440000000",
            "email": "aa@aa.com"
        },
        "identifier": {
            "scheme": "UA-EDR",
            "id": "00037256",
            "legalName": "Назва організації"
        },
        "kind": "general",
        "address": {
            "countryName": "Україна",
            "postalCode": "01220",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова, 11, корпус 1",
        },
        "name": "Державне управління справами"
    },
    "additionalClassifications": [
        {
            "scheme": "ДК003",
            "id": "17.21.1",
            "description": "папір і картон гофровані, паперова й картонна тара"
        }
    ],
    "classification": {
        "scheme": "ДК021",
        "description": "Mustard seeds",
        "id": "03111600-8"
    },
    "title": "Узагальнена назва закупівлі",
    "description": "Назва предмета закупівлі",
    "qualificationPeriod": {"endDate": (now + timedelta(days=120)).isoformat()}
}

test_framework_dps_config = {
    "restrictedDerivatives": False,
}

test_dps_documents = [
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
        "telephone": "+0440000000",
        "email": "aa@aa.com",
    },
    "scale": "micro"
}

test_submission_data = {
    "tenderers": [tenderer],
}

test_submission_config = {
    "restricted": False,
}

ban_milestone_data = {
    "type": "ban"
}

ban_milestone_data_with_documents = {
    "type": "ban",
    "documents": [
        {
            "hash": "md5:00000000000000000000000000000000",
            "title": "milestone.doc",
            "format": "application/msword",
            "datePublished": "2020-09-08T01:00:00+03:00",
            "id": "cd52b90af77e4f5b8cb0f210e83987b5",
            "dateModified": "2020-09-08T01:00:00+03:00"
        }
    ]
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    initial_auth = ("Basic", ("broker", ""))


class BaseFrameworkWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_framework_dps_data
    initial_config = test_framework_dps_config
    framework_class = Framework
    framework_type = DPS_TYPE
    docservice = False
    periods = PERIODS

    def create_framework(self, data=None, config=None):
        data = data if data is not None else deepcopy(self.initial_data)
        config = config if config is not None else deepcopy(self.initial_config)

        response = self.app.post_json("/frameworks", {
            "data": data,
            "config": config,
        })
        self.framework_token = response.json["access"]["token"]
        self.framework_id = response.json["data"]["id"]
        self.assertEqual(response.json["data"]["frameworkType"], self.framework_type)
        return response

    def activate_framework(self):
        with freeze_time((get_now() - timedelta(hours=1)).isoformat()):
            response = self.app.patch_json(
                "/frameworks/{}?acc_token={}".format(self.framework_id, self.framework_token),
                {"data": {"status": "active"}}
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["frameworkType"], self.framework_type)
        return response

    def save_changes(self):
        if self.framework_document_patch:
            patch = apply_data_patch(self.framework_document, self.framework_document_patch)
            self.framework_document.update(patch)
            self.mongodb.frameworks.save(Framework(self.framework_document))
            self.framework_document = self.mongodb.frameworks.get(self.framework_id)
            self.framework_document_patch = {}


class FrameworkContentWebTest(BaseFrameworkWebTest):
    initial_status = None

    def setUp(self):
        super(FrameworkContentWebTest, self).setUp()
        self.create_framework()


class BaseDSFrameworkContentWebTest(FrameworkContentWebTest):
    docservice = True


class BaseSubmissionContentWebTest(FrameworkContentWebTest):
    initial_submission_data = None
    initial_submission_config = test_submission_config

    def get_submission(self, role):
        with change_auth(self.app, ("Basic", (role, ""))):
            url = "/submissions/{}".format(self.submission_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["submissionType"], self.framework_type)
        return response

    def set_submission_status(self, status, extra=None):
        self.now = get_now()
        self.submission_document = self.mongodb.submissions.get(self.submission_id)
        self.submission_document_patch = {"status": status}
        if extra:
            self.submission_document_patch.update(extra)
        self.save_submission_changes()
        return self.get_submission("chronograph")

    def save_submission_changes(self):
        if self.submission_document_patch:
            patch = apply_data_patch(self.submission_document, self.submission_document_patch)
            self.submission_document.update(patch)
            self.mongodb.submissions.save(Submission(self.submission_document))
            self.submission_document = self.mongodb.submissions.get(self.submission_id)
            self.submission_document_patch = {}

    def create_submission(self, data=None, config=None):
        data = data if data is not None else deepcopy(self.initial_submission_data)
        config = config if config is not None else deepcopy(self.initial_submission_config)
        data["frameworkID"] = self.framework_id
        response = self.app.post_json("/submissions", {
            "data": data,
            "config": config,
        })
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

    def activate_qualification(self):
        response = self.app.post(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            upload_files=[("file", "name  name.doc", b"content")]
        )
        self.assertEqual(response.status, "201 Created")
        response = self.app.patch_json(
            f"/qualifications/{self.qualification_id}?acc_token={self.framework_token}",
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["qualificationType"], self.framework_type)
        return response


    def setUp(self):
        super(BaseSubmissionContentWebTest, self).setUp()
        self.initial_submission_data["frameworkID"] = self.framework_id
        self.activate_framework()
    def tearDown(self):
        super(BaseSubmissionContentWebTest, self).tearDown()


class SubmissionContentWebTest(BaseSubmissionContentWebTest):
    def setUp(self):
        super(SubmissionContentWebTest, self).setUp()
        self.create_submission()


class BaseAgreementContentWebTest(SubmissionContentWebTest):
    def set_agreement_status(self, status, extra=None):
        self.now = get_now()
        self.agreement_document = self.mongodb.agreements.get(self.agreement_id)
        self.agreement_document_patch = {"status": status}
        if extra:
            self.agreement_document_patch.update(extra)
        self.save_agreement_changes()
        return self.get_agreement("view")

    def save_agreement_changes(self):
        if self.agreement_document_patch:
            patch = apply_data_patch(self.agreement_document, self.agreement_document_patch)
            self.agreement_document.update(patch)
            self.mongodb.agreements.save(Agreement(self.agreement_document))
            self.agreement_document = self.mongodb.agreements.get(self.agreement_id)
            self.agreement_document_patch = {}

    def get_agreement(self, role=None):
        with change_auth(self.app, self.get_auth(role)):
            url = "/agreements/{}".format(self.agreement_id)
            response = self.app.get(url)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["agreementType"], self.framework_type)
        return response

    def check_chronograph(self, data=None):
        with change_auth(self.app, ("Basic", ("chronograph", ""))):
            url = "/agreements/{}".format(self.agreement_id)
            data = data or {"data": {"id": self.agreement_id}}
            response = self.app.patch_json(url, data)
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
        return response

    def set_contract_status(self, status):
        self.now = get_now()
        self.agreement_document = self.mongodb.agreements.get(self.agreement_id)
        self.agreement_document_patch = deepcopy(self.agreement_document)
        for contract in self.agreement_document_patch["contracts"]:
            if contract["id"] == self.contract_id:
                contract["status"] = status
        self.save_agreement_changes()
        return self.get_agreement("view")


class AgreementContentWebTest(BaseAgreementContentWebTest):
    def setUp(self):
        super().setUp()
        response = self.activate_submission()
        self.activate_qualification()
        response = self.get_framework()
        self.agreement_id = response.json["data"]["agreementID"]
        response = self.get_agreement()
        self.contract_id = response.json["data"]["contracts"][0]["id"]


class MilestoneContentWebTest(AgreementContentWebTest):
    def setUp(self):
        super().setUp()
        response = self.create_milestone()
        self.milestone_id = response.json["data"]["id"]

    def create_milestone(self):
        response = self.app.post_json(
            f"/agreements/{self.agreement_id}/contracts/{self.contract_id}/milestones?acc_token={self.framework_token}",
            {"data": self.initial_milestone_data}
        )
        self.assertEqual(response.status, "201 Created")
        return response
