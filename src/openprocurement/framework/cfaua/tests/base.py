import os.path
from copy import deepcopy

from openprocurement.framework.cfaua.tests.data import TEST_CHANGE, test_agreement_data
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
        super().setUp()
        self.create_agreement()

    def create_agreement(self):
        data = deepcopy(self.initial_data)
        if documents := data.get("documents"):
            for doc in documents:
                doc["url"] = self.generate_docservice_url()
                doc["hash"] = "md5:00000000000000000000000000000000"
        with change_auth(self.app, ("Basic", ("agreements", ""))):
            response = self.app.post_json("/agreements", {"data": data})
        self.agreement = response.json["data"]
        self.agreement_id = self.agreement["id"]

    def tearDown(self):
        # del self.db[self.agreement_id]
        super().tearDown()


class BaseAgreementContentWebTest(BaseAgreementWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.patch_json(
            "/agreements/{}/credentials?acc_token={}".format(self.agreement_id, self.initial_data["tender_token"]),
            {"data": {}},
        )
        self.agreement_token = response.json["access"]["token"]


class BaseDSAgreementContentWebTest(BaseAgreementContentWebTest):
    docservice = True
