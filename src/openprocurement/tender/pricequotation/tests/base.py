import os

from datetime import datetime
from uuid import uuid4

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.core.tests.base import BaseCoreWebTest
from openprocurement.api.constants import TZ
from openprocurement.api.context import set_now
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER
from openprocurement.tender.belowthreshold.utils import prepare_tender_item_for_contract
from openprocurement.tender.pricequotation.models import PriceQuotationTender
from openprocurement.tender.pricequotation.tests.data import *
from openprocurement.framework.electroniccatalogue.models import Agreement


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderWebTest(BaseCoreWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_pq_data
    initial_config = test_tender_pq_config
    initial_status = None
    maxDiff = None
    initial_agreement_data = test_agreement_pq_data
    agreement_id = initial_agreement_data["_id"]

    initial_bids = None
    initial_auth = ("Basic", ("broker", ""))
    docservice = True
    min_bids_number = MIN_BIDS_NUMBER
    # Statuses for test, that will be imported from others procedures
    primary_tender_status = "draft.publishing"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "active.qualification"
    )  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_add_actions_status = (
        "active.tendering"
    )  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.tendering"
    )  # status, in which updating tender questions is forbidden
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"
    )  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"
    )  # status, in which adding document to tender auction is forbidden
    periods = PERIODS
    meta_initial_bids = test_tender_pq_bids
    tender_class = PriceQuotationTender

    def setUp(self):
        super(BaseTenderWebTest, self).setUp()
        if PQ_MULTI_PROFILE_RELEASED:
            self.create_agreement()
            self.initial_data["agreement"] = {"id": self.agreement_id}

    def tearDown(self):
        if PQ_MULTI_PROFILE_RELEASED:
            self.delete_agreement()
        super(BaseTenderWebTest, self).tearDown()

    def generate_awards(self, status, startend):
        bids = self.tender_document.get("bids", []) or self.tender_document_patch.get("bids", [])
        awardPeriod_startDate = (self.now + self.periods[status][startend]["awardPeriod"]["startDate"]).isoformat()
        if "awards" not in self.tender_document and bids:
            self.award_ids = []
            self.tender_document_patch["awards"] = []
            id_ = uuid4().hex
            award = {
                "status": "pending",
                "suppliers": bids[0]["tenderers"],
                "bid_id": bids[0]["id"],
                "value": bids[0]["value"],
                "date": awardPeriod_startDate,
                # "documents": [],
                "id": id_,
            }
            self.tender_document_patch["awards"].append(award)
            self.award_ids.append(id_)
            self.save_changes()

    def activate_awards(self):
        awards = self.tender_document.get("awards", [])
        if awards:
            for award in awards:
                if award["status"] == "pending":
                    award.update({"status": "active"})
            self.tender_document_patch.update({"awards": awards})
            self.save_changes()

    def generate_bids(self, status, startend):
        tenderPeriod_startDate = self.now + self.periods[status][startend]["tenderPeriod"]["startDate"]
        bids = self.tender_document.get("bids", [])
        if self.initial_bids and not bids:
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
            self.save_changes()
        response = self.app.get('/tenders/{}/bids'.format(self.tender_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.initial_bids = response.json["data"]

    def generate_contract(self):
        awards = self.tender_document.get("awards", [])
        contracts = self.tender_document.get("contracts", [])

        if not contracts:
            for award in reversed(awards):
                if award["status"] == "active":
                    if award["value"]["valueAddedTaxIncluded"]:
                        amount_net = float(award["value"]["amount"]) - 1
                    else:
                        amount_net = award["value"]["amount"]
                    prepared_items = [prepare_tender_item_for_contract(i) for i in self.tender_document["items"]]
                    contract = {
                        "id": uuid4().hex,
                        "title": "contract title",
                        "description": "contract description",
                        "awardID": award["id"],
                        "value": {
                            "amount": award["value"]["amount"],
                            "amountNet": amount_net,
                            "currency": award["value"]["currency"],
                            "valueAddedTaxIncluded": award["value"]["valueAddedTaxIncluded"],
                        },
                        "suppliers": award["suppliers"],
                        "status": "pending",
                        "contractID": "UA-2017-06-21-000001-1",
                        "date": datetime.now(TZ).isoformat(),
                        "items": prepared_items,
                    }
                    self.contract_id = contract["id"]
                    self.tender_document_patch.update({"contracts": [contract]})
            self.save_changes()

    def set_status(self, status, startend="start", extra=None):
        self.now = get_now()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.patch_tender_bot()
        if status == "active.tendering":
            self.update_periods(status, startend)
        elif status == "active.qualification":
            self.update_periods(status, startend)
            self.generate_bids(status, startend)
            self.generate_awards(status, startend)
        elif status == "active.awarded":
            self.update_periods(status, startend)
            self.generate_bids(status, startend)
            self.generate_awards(status, startend)
            self.activate_awards()
            self.generate_contract()
        elif status == "complete":
            self.update_periods(status, startend)
            self.generate_bids(status, startend)
            self.generate_awards(status, startend)
            self.activate_awards()
            self.generate_contract()
        self.save_changes()
        return self.get_tender("chronograph")

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
            'value': value
        })
        self.save_changes()

    @property
    def tender_token(self):
        data = self.mongodb.tenders.get(self.tender_id)
        award = data['awards'][-1] if data.get('awards') else None
        if award and award['status'] == 'pending':
            bid = [b for b in data['bids'] if b['id'] == award['bid_id']][0]
            return bid['owner_token']
        else:
            return data['owner_token']

    def create_tender(self):
        data = deepcopy(self.initial_data)
        config = deepcopy(self.initial_config)
        if PQ_MULTI_PROFILE_RELEASED:
            data["agreement"] = {"id": self.agreement_id}
        data["criteria"] = getattr(self, "test_criteria", test_tender_pq_criteria)

        response = self.app.post_json("/tenders", {"data": data, "config": config})
        tender = response.json["data"]
        self.tender_id = tender["id"]
        status = tender["status"]
        if self.initial_status and self.initial_status != status:
            self.set_status(self.initial_status)

    def create_agreement(self):
        if self.mongodb.agreements.get(self.agreement_id):
            self.delete_agreement()
        agreement = Agreement(test_agreement_pq_data)
        agreement.dateModified = get_now().isoformat()
        set_now()
        self.mongodb.agreements.save(agreement, insert=True)

    def delete_agreement(self):
        self.mongodb.agreements.delete(self.agreement_id)


class TenderContentWebTest(BaseTenderWebTest):
    initial_status = None
    initial_bids = None
    need_tender = True

    def setUp(self):
        super(TenderContentWebTest, self).setUp()
        if self.need_tender:
            self.create_tender()
