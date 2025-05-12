import os
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.context import set_request_now
from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.contracting.core.tests.base import BaseContractTest
from openprocurement.contracting.econtract.tests.data import (
    test_contract_data,
    test_contract_data_two_items,
    test_signer_info,
)
from openprocurement.contracting.econtract.tests.utils import create_contract
from openprocurement.tender.core.tests.mock import patch_market
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.pricequotation.tests.data import (
    PERIODS,
    test_agreement_pq_data,
    test_tender_pq_bids,
    test_tender_pq_category,
    test_tender_pq_config,
    test_tender_pq_criteria,
    test_tender_pq_data,
    test_tender_pq_short_profile,
    test_tender_pq_shortlisted_firms,
)


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseEContractTest(BaseContractTest):
    relative_to = os.path.dirname(__file__)

    initial_tender_data = test_tender_pq_data
    initial_tender_config = test_tender_pq_config
    initial_agreement_data = test_agreement_pq_data
    agreement_id = initial_agreement_data["_id"]

    def setUp(self):
        super().setUp()
        self.create_agreement()
        self.initial_tender_data["agreement"] = {"id": self.agreement_id}
        self.create_tender()

    def tearDown(self):
        self.delete_agreement()
        self.delete_tender()
        super().tearDown()

    def generate_awards(self, status, startend):
        bids = self.tender_document.get("bids", [])
        awardPeriod_startDate = (self.now + PERIODS[status][startend]["awardPeriod"]["startDate"]).isoformat()
        self.tender_document_patch["awards"] = []
        id_ = uuid4().hex
        award = {
            "status": "active",
            "suppliers": bids[0]["tenderers"],
            "bid_id": bids[0]["id"],
            "value": bids[0]["value"],
            "date": awardPeriod_startDate,
            # "documents": [],
            "id": id_,
        }
        self.award_id = id_
        self.tender_document_patch["awards"].append(award)
        self.save_tender_changes()

    def generate_bids(self, status, startend):
        tenderPeriod_startDate = self.now + PERIODS[status][startend]["tenderPeriod"]["startDate"]
        self.tender_document_patch["bids"] = []
        self.initial_bids_tokens = []
        for position, bid in enumerate(test_tender_pq_bids):
            bid = deepcopy(bid)
            token = uuid4().hex
            bid.update(
                {
                    "id": uuid4().hex,
                    "date": (tenderPeriod_startDate + timedelta(seconds=(position + 1))).isoformat(),
                    "owner_token": token,
                    "status": "draft",
                    "owner": "broker",
                }
            )
            self.tender_document_patch["bids"].append(bid)
            self.initial_bids_tokens.append(token)
        self.bid_token = self.initial_bids_tokens[0]
        self.save_tender_changes()

    def generate_tender_data(self, startend="start", extra=None):
        self.now = get_now()
        status = "active.awarded"
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.patch_tender_bot()
        # self.update_periods(status, startend)
        self.generate_bids(status, startend)
        self.generate_awards(status, startend)
        self.generate_contracts()
        self.save_tender_changes()

    def patch_tender_bot(self):
        items = deepcopy(self.initial_tender_data["items"])
        for item in items:
            item.update(
                {
                    "classification": test_tender_pq_short_profile["classification"],
                    "unit": test_tender_pq_short_profile["unit"],
                }
            )
        value = deepcopy(test_tender_pq_short_profile['value'])
        amount = sum(item["quantity"] for item in items) * test_tender_pq_short_profile['value']['amount']
        value["amount"] = amount
        # criteria = getattr(self, "test_criteria", test_short_profile['criteria'])
        self.tender_document_patch.update(
            {
                "shortlistedFirms": test_tender_pq_shortlisted_firms,
                # 'criteria': criteria,
                "items": items,
                "value": value,
            }
        )

    def save_tender_changes(self):
        if self.tender_document_patch:
            patch = apply_data_patch(self.tender_document, self.tender_document_patch)
            self.tender_document.update(patch)
            self.mongodb.tenders.save(self.tender_document)
            self.tender_document = self.mongodb.tenders.get(self.tender_id)
            self.tender_document_patch = {}

    @patch_market(test_tender_pq_short_profile, test_tender_pq_category)
    def create_tender(self):
        auth = self.app.authorization
        self.app.authorization = ("Basic", ("broker", ""))
        data = self.initial_tender_data
        config = self.initial_tender_config
        data["agreement"] = {"id": self.agreement_id}

        test_criteria = deepcopy(test_tender_pq_criteria)
        set_tender_criteria(test_criteria, data.get("lots", []), data.get("items", []))

        data["criteria"] = getattr(self, "test_criteria", test_criteria)

        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender_id = tender["id"]
        self.tender_token = response.json["access"]["token"]
        self.generate_tender_data()
        self.app.authorization = auth

    def create_agreement(self):
        if self.mongodb.agreements.get(self.agreement_id):
            self.delete_agreement()

        agreement = deepcopy(self.initial_agreement_data)
        agreement["dateModified"] = get_now().isoformat()
        set_request_now()
        self.mongodb.agreements.save(agreement, insert=True)

    def generate_contracts(self):
        awards = self.tender_document.get("awards", [])
        tender_contracts = []
        self.tender_contracts_ids = []
        for award in reversed(awards):
            if award["status"] == "active":
                tender_contract_data = {
                    "id": uuid4().hex,
                    "awardID": award["id"],
                    "status": "pending",
                }
                tender_contracts.append(tender_contract_data)
                self.tender_contracts_ids.append(test_contract_data["id"])
                if hasattr(self, "initial_data"):
                    self.initial_data = self.initial_data.copy()
                    self.initial_data["awardID"] = award["id"]
                    self.initial_data["tender_id"] = self.tender_id
                    self.initial_data["id"] = tender_contract_data["id"]
        self.tender_document_patch.update({"contracts": tender_contracts})
        self.save_tender_changes()

    def delete_agreement(self):
        self.mongodb.agreements.delete(self.agreement_id)

    def delete_tender(self):
        self.mongodb.tenders.delete(self.tender_id)


class BaseEContractWebTest(BaseEContractTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_contract_data
    initial_status = "pending"
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        self.create_agreement()
        self.initial_tender_data["agreement"] = {"id": self.agreement_id}
        self.create_contract()

    def tearDown(self):
        self.delete_agreement()
        self.delete_tender()
        self.delete_contract()
        super().tearDown()

    def save_contract_changes(self):
        if self.contract_document_patch:
            patch = apply_data_patch(self.contract_document, self.contract_document_patch)
            self.contract_document.update(patch)
            self.mongodb.contracts.save(self.contract_document)
            self.contract_document = self.mongodb.contracts.get(self.contract_id)
            self.contract_document_patch = {}

    def set_status(self, status):
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

    def create_contract(self):
        for tender_contract in self.tender_document.get("contracts", ""):
            # suppliers = deepcopy(award["suppliers"])
            # for i in suppliers:
            #     for attr in ("contactPoint", "scale", "kind"):
            #         if attr in i:
            #             del i[attr]

            contract = self.initial_data
            contract.update(tender_contract)
            contract.update(
                {
                    "tender_id": self.tender_id,
                    # "suppliers": suppliers,
                    "owner": self.tender_document["owner"],
                    "tender_token": self.tender_document["owner_token"],
                    "bid_owner": "broker",
                    "bid_token": self.initial_bids_tokens[0],
                }
            )
            # if "items" in self.initial_data:
            #     contract["items"] = prepared_items
            self.contract_id = contract["id"]
            self.contract = create_contract(self, contract)
            self.set_status(self.initial_status)

    def delete_contract(self):
        if self.contract_id:
            self.mongodb.contracts.delete(self.contract_id)


class BaseEContractContentWebTest(BaseEContractWebTest):
    def setUp(self):
        super().setUp()
        response = self.app.patch_json(
            "/contracts/{}/credentials?acc_token={}".format(self.contract_id, self.initial_data["tender_token"]),
            {"data": {}},
        )
        self.contract_token = response.json["access"]["token"]


class BaseEContractWebTestTwoItems(BaseEContractWebTest):
    initial_data = test_contract_data_two_items
