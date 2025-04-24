import os
from datetime import datetime
from uuid import uuid4

from openprocurement.api.constants import TZ
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.constants import MIN_BIDS_NUMBER
from openprocurement.tender.core.tests.base import BaseCoreWebTest
from openprocurement.tender.core.tests.mock import patch_market
from openprocurement.tender.pricequotation.tests.data import (
    PERIODS,
    test_agreement_pq_data,
    test_tender_pq_bids,
    test_tender_pq_category,
    test_tender_pq_config,
    test_tender_pq_criteria,
    test_tender_pq_data,
    test_tender_pq_short_profile,
)


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
    initial_profile = test_tender_pq_short_profile
    initial_category = test_tender_pq_category

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
                "id": id_,
            }
            if status in ("active.awarded", "complete"):
                award["documents"] = [
                    {
                        "id": uuid4().hex,
                        "title": "sign.p7s",
                        "documentType": "notice",
                        "url": self.generate_docservice_url(),
                        "hash": "md5:" + "0" * 32,
                        "format": "sign/pkcs7-signature",
                        "documentOf": "tender",
                        "datePublished": datetime.now(TZ).isoformat(),
                    }
                ]
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
                        {"data": {"status": "active", "qualified": True}},
                    )
                    self.assertEqual(response.status, "200 OK")
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}

    def set_status(self, status, startend="start", extra=None):
        self.now = get_now()
        self.tender_document = self.mongodb.tenders.get(self.tender_id)
        self.tender_document_patch = {"status": status}
        self.save_changes()  # apply status
        self.update_periods(status, startend)

        if status == "active.qualification":
            self.activate_bids()
            self.generate_awards(status, startend)
        elif status == "active.awarded":
            self.activate_bids()
            self.generate_awards(status, startend)
            self.activate_awards(status)
        elif status == "complete":
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

    @tender_token.setter
    def tender_token(self, value):
        pass

    def create_tender(self):
        with patch_market(self.initial_profile, self.initial_category):
            super().create_tender()


class TenderContentWebTest(BaseTenderWebTest):
    initial_status = None
    initial_bids = None

    initial_criteria = test_tender_pq_criteria

    def setUp(self):
        super().setUp()
        self.create_tender()
