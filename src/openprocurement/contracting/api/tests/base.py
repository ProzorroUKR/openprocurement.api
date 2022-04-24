# -*- coding: utf-8 -*-
import os
from copy import deepcopy

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.contracting.api.tests.data import (
    test_contract_data,
    test_contract_data_two_items,
)
from openprocurement.tender.core.tests.base import BaseWebTest as BaseCoreWebTest


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseContractTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)


class BaseContractWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_contract_data
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(BaseContractWebTest, self).setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_data)

        orig_auth = self.app.authorization
        self.app.authorization = ("Basic", ("contracting", ""))
        response = self.app.post_json("/contracts", {"data": data})
        self.contract = response.json["data"]
        self.contract_id = self.contract["id"]
        self.app.authorization = orig_auth


class BaseContractContentWebTest(BaseContractWebTest):
    def setUp(self):
        super(BaseContractContentWebTest, self).setUp()
        response = self.app.patch_json(
            "/contracts/{}/credentials?acc_token={}".format(self.contract_id, self.initial_data["tender_token"]),
            {"data": {}},
        )
        self.contract_token = response.json["access"]["token"]


class BaseContractWebTestTwoItems(BaseContractWebTest):
    initial_data = test_contract_data_two_items
