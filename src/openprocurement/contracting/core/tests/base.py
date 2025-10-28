import os
from copy import deepcopy

from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.utils import get_now
from openprocurement.contracting.core.tests.data import test_signer_info
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest as BaseCoreWebTest,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_bids,
    test_tender_pq_supplier,
)


class BaseContractTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_status = "active.qualification"
    initial_bids = test_tender_pq_bids

    def setUp(self):
        super().setUp()
        self.create_award()

    def save_tender_changes(self):
        if self.tender_document_patch:
            patch = apply_data_patch(self.tender_document, self.tender_document_patch)
            self.tender_document.update(patch)
            self.mongodb.tenders.save(self.tender_document)
            self.tender_document = self.mongodb.tenders.get(self.tender_id)
            self.tender_document_patch = {}

    def create_award(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/awards",
            {
                "data": {
                    "suppliers": [test_tender_pq_supplier],
                    "status": "pending",
                    "bid_id": self.initial_bids[0]["id"],
                    "value": {"currency": "UAH", "amount": 450.0, "valueAddedTaxIncluded": True},
                }
            },
        )
        self.app.authorization = auth
        self.award = response.json["data"]
        self.award_id = self.award["id"]


class BaseContractWebTest(BaseContractTest):
    relative_to = os.path.dirname(__file__)
    initial_contract_status = "pending"
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        self.activate_award()

    def activate_award(self):
        self.add_sign_doc(self.tender_id, self.tender_token, docs_url=f"/awards/{self.award_id}/documents")
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
            {"data": {"status": "active", "qualified": True}},
        )

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.contract_id = response.json["data"]["contracts"][0]["id"]
        response = self.app.get(f"/contracts/{self.contract_id}")
        self.contract = response.json["data"]
        self.bid_token = self.initial_bids_tokens[self.award["bid_id"]]

        response = self.app.patch_json(
            f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
            {"data": {"value": {**self.contract["value"], "amountNet": 440}}},
        )
        self.contract = response.json["data"]

    def save_contract_changes(self):
        if self.contract_document_patch:
            patch = apply_data_patch(self.contract_document, self.contract_document_patch)
            self.contract_document.update(patch)
            self.mongodb.contracts.save(self.contract_document)
            self.contract_document = self.mongodb.contracts.get(self.contract_id)
            self.contract_document_patch = {}

    def set_contract_status(self, status):
        self.now = get_now()
        self.contract_document = self.mongodb.contracts.get(self.contract_id)
        self.contract_document_patch = {"status": status}
        if status in ("active", "terminated"):
            self.contract_document_patch.update(
                {
                    "suppliers": [{**self.contract_document["suppliers"][0], "signerInfo": test_signer_info}],
                    "buyer": {**self.contract_document["buyer"], "signerInfo": test_signer_info},
                    "dateSigned": get_now().isoformat(),
                }
            )
            self.tender_document = self.mongodb.tenders.get(self.tender_id)
            contracts = deepcopy(self.tender_document["contracts"])
            contract = [i for i in self.tender_document["contracts"] if self.contract_id == i["id"]][0]
            contract["status"] = "active"
            self.tender_document_patch = {"status": "complete", "contracts": contracts}
            self.save_tender_changes()
        self.save_contract_changes()

    def prepare_contract_for_signing(self):
        # add required fields
        response = self.app.patch_json(
            f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
            {
                "data": {
                    "contractNumber": "123",
                    "period": {
                        "startDate": "2016-03-18T18:47:47.155143+02:00",
                        "endDate": "2016-05-18T18:47:47.155143+02:00",
                    },
                }
            },
        )
        self.assertEqual(response.status, "200 OK")

        # add signerInfo for supplier
        self.app.put_json(
            f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        # add signerInfo for buyer
        self.app.put_json(
            f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.contract_token}",
            {"data": test_signer_info},
        )


class BaseContractContentWebTest(BaseContractWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.patch_json(
            "/contracts/{}/credentials?acc_token={}".format(self.contract_id, self.tender_token),
            {"data": {}},
        )
        self.contract_token = response.json["access"]["token"]
        self.set_contract_status(self.initial_contract_status)
