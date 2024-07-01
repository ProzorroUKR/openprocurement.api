import os
from uuid import uuid4

from mock import Mock, patch

from openprocurement.api.context import set_now
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER
from openprocurement.tender.core.tests.base import BaseCoreWebTest
from openprocurement.tender.pricequotation.tests.data import *


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
    primary_tender_status = "active.tendering"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "active.qualification"  # status, in which operations with tender documents (adding, updating) are forbidden
    )
    forbidden_question_add_actions_status = "active.tendering"  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.tendering"  # status, in which updating tender questions is forbidden
    )
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    )
    forbidden_auction_document_create_actions_status = (
        "active.tendering"  # status, in which adding document to tender auction is forbidden
    )
    periods = PERIODS
    meta_initial_bids = test_tender_pq_bids

    def setUp(self):
        super().setUp()
        self.create_agreement()
        self.initial_data["agreement"] = {"id": self.agreement_id}

    def tearDown(self):
        self.delete_agreement()
        super().tearDown()

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

    def activate_awards(self, status):
        self.tender_document_patch["status"] = "active.awarded"
        self.save_changes()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)

        awards = self.tender_document.get("awards", [])
        if awards:
            for award in awards:
                if award["status"] == "pending":
                    response = self.app.patch_json(
                        f"/tenders/{self.tender_id}/awards/{award['id']}?acc_token={self.tender_token}",
                        {"data": {"status": "active"}},
                    )
                    self.assertEqual(response.status, "200 OK")
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}

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

    def activate_bids(self):
        if bids := self.tender_document.get("bids", ""):
            for bid in bids:
                if bid["status"] in ("draft", "pending"):
                    bid.update({"status": "active"})
            self.tender_document_patch.update({"bids": bids})

    def set_status(self, status, startend="start", extra=None):
        self.now = get_now()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.save_changes()  # apply status
        if status == "active.tendering":
            self.update_periods(status, startend)
        elif status == "active.qualification":
            self.update_periods(status, startend)
            self.generate_bids(status, startend)
            self.activate_bids()
            self.generate_awards(status, startend)
        elif status == "active.awarded":
            self.update_periods(status, startend)
            self.generate_bids(status, startend)
            self.activate_bids()
            self.generate_awards(status, startend)
            self.activate_awards(status)
        elif status == "complete":
            self.update_periods(status, startend)
            self.generate_bids(status, startend)
            self.activate_bids()
            self.generate_awards(status, startend)
            self.activate_awards(status)
        if extra:
            self.tender_document_patch.update(extra)
        self.save_changes()
        return self.get_tender()

    @property
    def tender_token(self):
        data = self.mongodb.tenders.get(self.tender_id)
        return data['owner_token']

    @patch(
        "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
        Mock(return_value=test_tender_pq_short_profile),
    )
    @patch(
        "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
        Mock(return_value=test_tender_pq_category),
    )
    def create_tender(self):
        data = deepcopy(self.initial_data)
        config = deepcopy(self.initial_config)
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
        agreement = test_agreement_pq_data
        agreement["dateModified"] = get_now().isoformat()
        set_now()
        self.mongodb.agreements.save(agreement, insert=True)

    def delete_agreement(self):
        self.mongodb.agreements.delete(self.agreement_id)


class TenderContentWebTest(BaseTenderWebTest):
    initial_status = None
    initial_bids = None
    need_tender = True

    def setUp(self):
        super().setUp()
        if self.need_tender:
            self.create_tender()
