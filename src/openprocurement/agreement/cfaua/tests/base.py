# -*- coding: utf-8 -*-
import os.path
import json
from copy import deepcopy
from uuid import uuid4
from hashlib import sha512

from datetime import datetime
from openprocurement.api.utils import get_now
from openprocurement.tender.core.tests.base import BaseWebTest

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "data/agreement.json")) as _in:
    TEST_AGREEMENT = json.load(_in)


with open(os.path.join(here, "data/documents.json")) as _in:
    TEST_DOCUMENTS = json.load(_in)


with open(os.path.join(here, "data/features.json")) as _in:
    TEST_FEATURES = json.load(_in)

with open(os.path.join(here, "data/change.json")) as _in:
    TEST_CHANGE = json.load(_in)

now = datetime.now()

test_tender_token = uuid4().hex
test_agreement_data = deepcopy(TEST_AGREEMENT)
test_agreement_data["dateSigned"] = get_now().isoformat()
test_agreement_data["tender_token"] = sha512(test_tender_token).hexdigest()

test_agreement_data_wo_items = deepcopy(test_agreement_data)
del test_agreement_data_wo_items["items"]


documents = deepcopy(TEST_DOCUMENTS)


class BaseAgreementWebTest(BaseWebTest):
    docservice = False
    initial_data = test_agreement_data
    initial_change = TEST_CHANGE
    relative_to = os.path.dirname(__file__)

    def setUp(self):
        super(BaseAgreementWebTest, self).setUp()
        self.create_agreement()

    def create_agreement(self):
        data = deepcopy(self.initial_data)

        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("agreements", ""))
        response = self.app.post_json("/agreements", {"data": data})
        self.agreement = response.json["data"]
        # self.agreement_token = response.json['access']['token']
        self.agreement_id = self.agreement["id"]
        self.app.authorization = orig_auth

    def tearDown(self):
        del self.db[self.agreement_id]
        super(BaseAgreementWebTest, self).tearDown()


class BaseAgreementContentWebTest(BaseAgreementWebTest):
    def setUp(self):
        super(BaseAgreementContentWebTest, self).setUp()
        response = self.app.patch_json(
            "/agreements/{}/credentials?acc_token={}".format(self.agreement_id, self.initial_data["tender_token"]),
            {"data": {}},
        )
        self.agreement_token = response.json["access"]["token"]
