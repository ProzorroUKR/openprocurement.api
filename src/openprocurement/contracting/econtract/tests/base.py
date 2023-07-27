import os
from copy import deepcopy

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.contracting.econtract.tests.data import (
    test_contract_data,
    test_contract_data_two_items,
)
from openprocurement.contracting.econtract.tests.utils import create_contract
from openprocurement.contracting.api.tests.base import BaseContractTest


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseEContractTest(BaseContractTest):
    relative_to = os.path.dirname(__file__)


class BaseEContractWebTest(BaseEContractTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_contract_data
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        self.create_contract()

    def create_contract(self):
        data = deepcopy(self.initial_data)

        self.contract = create_contract(self, data)
        self.contract_id = self.contract["id"]


class BaseEContractContentWebTest(BaseEContractWebTest):
    def setUp(self):
        super(BaseEContractContentWebTest, self).setUp()
        response = self.app.patch_json(
            "/contracts/{}/credentials?acc_token={}".format(self.contract_id, self.initial_data["tender_token"]),
            {"data": {}},
        )
        self.contract_token = response.json["access"]["token"]


class BaseEContractWebTestTwoItems(BaseEContractWebTest):
    initial_data = test_contract_data_two_items
