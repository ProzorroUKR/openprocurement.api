import os
from uuid import uuid4

from openprocurement.api.utils import apply_data_patch
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.contracting.econtract.tests.data import (
    test_contract_data,
    test_contract_data_two_items,
)
from openprocurement.contracting.econtract.tests.utils import create_contract
from openprocurement.contracting.api.tests.base import BaseContractTest
from openprocurement.tender.pricequotation.tests.data import *
from openprocurement.framework.electroniccatalogue.models import Agreement
from openprocurement.tender.belowthreshold.utils import prepare_tender_item_for_contract
from openprocurement.api.context import set_now


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseEContractTest(BaseContractTest):
    relative_to = os.path.dirname(__file__)


class BaseEContractWebTest(BaseEContractTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_contract_data
    initial_tender_data = test_tender_pq_data
    initial_tender_config = test_tender_pq_config
    initial_agreement_data = test_agreement_pq_data
    agreement_id = initial_agreement_data["_id"]
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()
        if PQ_MULTI_PROFILE_RELEASED:
            self.create_agreement()
            self.initial_tender_data["agreement"] = {"id": self.agreement_id}
        self.create_tender()

    def tearDown(self):
        if PQ_MULTI_PROFILE_RELEASED:
            self.delete_agreement()
        self.delete_tender()
        self.delete_contract()
        super().tearDown()

    def generate_awards(self, status, startend):
        bids = self.tender_document.get("bids", [])
        awardPeriod_startDate = (self.now + PERIODS[status][startend]["awardPeriod"]["startDate"]).isoformat()
        self.award_ids = []
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

    def generate_contract(self):
        awards = self.tender_document.get("awards", [])

        for award in reversed(awards):
            if award["status"] == "active":
                if award["value"]["valueAddedTaxIncluded"]:
                    amount_net = float(award["value"]["amount"]) - 1
                else:
                    amount_net = award["value"]["amount"]
                prepared_items = [prepare_tender_item_for_contract(i) for i in self.tender_document["items"]]
                tender_contract_data = {
                    "id": uuid4().hex,
                    "awardID": award["id"],
                    "status": "pending",
                }

                suppliers = deepcopy(award["suppliers"])
                for i in suppliers:
                    for attr in ("contactPoint", "scale", "kind"):
                        if attr in i:
                            del i[attr]

                contract = self.initial_data
                contract.update(tender_contract_data)
                contract.update({
                    "value": {
                        "amount": award["value"]["amount"],
                        "amountNet": amount_net,
                        "currency": award["value"]["currency"],
                        "valueAddedTaxIncluded": award["value"]["valueAddedTaxIncluded"],
                    },
                    "tender_id": self.tender_id,
                    "suppliers": suppliers,
                    "items": prepared_items,
                    "owner": self.tender_document["owner"],
                    "tender_token": self.tender_document["owner_token"],
                    "bid_owner": "broker",
                    "bid_token": self.initial_bids_tokens[0]
                })
                contract.update(tender_contract_data)
                self.contract_id = contract["id"]
                self.tender_document_patch.update({"contracts": [tender_contract_data]})
                self.contract = create_contract(self, contract)
                self.save_tender_changes()
                break

    def generate_tender_data(self, startend="start", extra=None):
        self.now = get_now()
        status = "active.awarded"
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.patch_tender_bot()
        # self.update_periods(status, startend)
        self.generate_bids(status, startend)
        self.generate_awards(status, startend)
        self.generate_contract()
        self.save_tender_changes()

    def patch_tender_bot(self):
        items = deepcopy(self.initial_data["items"])
        for item in items:
            item.update({
                "classification": test_tender_pq_short_profile["classification"],
                "unit": test_tender_pq_short_profile["unit"]
            })
        value = deepcopy(test_tender_pq_short_profile['value'])
        amount = sum([item["quantity"] for item in items]) * test_tender_pq_short_profile['value']['amount']
        value["amount"] = amount
        # criteria = getattr(self, "test_criteria", test_short_profile['criteria'])
        self.tender_document_patch.update({
            "shortlistedFirms": test_tender_pq_shortlisted_firms,
            # 'criteria': criteria,
            "items": items,
            "value": value
        })

    def save_tender_changes(self):
        if self.tender_document_patch:
            patch = apply_data_patch(self.tender_document, self.tender_document_patch)
            self.tender_document.update(patch)
            self.mongodb.tenders.save(self.tender_document)
            self.tender_document = self.mongodb.tenders.get(self.tender_id)
            self.tender_document_patch = {}

    def create_tender(self):
        data = self.initial_tender_data
        config = self.initial_tender_config
        if PQ_MULTI_PROFILE_RELEASED:
            data["agreement"] = {"id": self.agreement_id}
        data["criteria"] = getattr(self, "test_criteria", test_tender_pq_criteria)

        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender_id = tender["id"]
        self.tender_token = response.json["access"]["token"]
        self.generate_tender_data()

    def create_agreement(self):
        if self.mongodb.agreements.get(self.agreement_id):
            self.delete_agreement()
        agreement = Agreement(self.initial_agreement_data)
        agreement.dateModified = get_now().isoformat()
        set_now()
        self.mongodb.agreements.save(agreement, insert=True)

    def delete_agreement(self):
        self.mongodb.agreements.delete(self.agreement_id)

    def delete_tender(self):
        self.mongodb.tenders.delete(self.tender_id)

    def delete_contract(self):
        if self.contract_id:
            self.mongodb.contracts.delete(self.contract_id)


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
