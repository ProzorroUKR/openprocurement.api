# -*- coding: utf-8 -*-
import os.path
from copy import deepcopy

from openprocurement.framework.cfaua.tests.data import (
    test_agreement_data,
    TEST_CHANGE,
)
from openprocurement.tender.core.tests.base import BaseWebTest
from openprocurement.tender.core.tests.utils import change_auth


class BaseAgreementTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
    docservice = False
    initial_auth = ("Basic", ("broker", ""))


class BaseAgreementWebTest(BaseAgreementTest):
    initial_data = test_agreement_data
    initial_change = TEST_CHANGE

    def setUp(self):
        super(BaseAgreementWebTest, self).setUp()
        self.create_agreement()

    def create_agreement(self):
        data = deepcopy(self.initial_data)
        with change_auth(self.app, ("Basic", ("agreements", ""))):
            response = self.app.post_json("/agreements", {"data": data})
        self.agreement = response.json["data"]
        self.agreement_id = self.agreement["id"]

    def tearDown(self):
        # del self.db[self.agreement_id]
        super(BaseAgreementWebTest, self).tearDown()


class BaseAgreementContentWebTest(BaseAgreementWebTest):
    def setUp(self):
        super(BaseAgreementContentWebTest, self).setUp()
        response = self.app.patch_json(
            "/agreements/{}/credentials?acc_token={}".format(self.agreement_id, self.initial_data["tender_token"]),
            {"data": {}},
        )
        self.agreement_token = response.json["access"]["token"]


class BaseDSAgreementContentWebTest(BaseAgreementContentWebTest):
    docservice = True
