# -*- coding: utf-8 -*-
import os

from datetime import timedelta
from copy import deepcopy
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_data as test_tender_data_api,
    test_features_tender_data,
    BaseTenderWebTest,
    test_bids as base_test_bids,
)
from openprocurement.tender.openua.models import Tender
from openprocurement.tender.openua.tests.periods import PERIODS

now = get_now()
test_tender_data = test_tender_ua_data = test_tender_data_api.copy()
test_tender_data["procurementMethodType"] = "aboveThresholdUA"
del test_tender_data["enquiryPeriod"]
test_tender_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_data["items"] = [
    {
        "description": u"футляри до державних нагород",
        "description_en": u"Cases for state awards",
        "classification": {"scheme": u"ДК021", "id": u"44617100-9", "description": u"Cartons"},
        "additionalClassifications": [
            {"scheme": u"ДКПП", "id": u"17.21.1", "description": u"папір і картон гофровані, паперова й картонна тара"}
        ],
        "unit": {"name": u"item", "code": u"44617100-9"},
        "quantity": 5,
        "deliveryDate": {
            "startDate": (now + timedelta(days=2)).isoformat(),
            "endDate": (now + timedelta(days=5)).isoformat(),
        },
        "deliveryAddress": {
            "countryName": u"Україна",
            "postalCode": "79000",
            "region": u"м. Київ",
            "locality": u"м. Київ",
            "streetAddress": u"вул. Банкова 1",
        },
    }
]
if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_bids = deepcopy(base_test_bids)

bid_update_data = {"selfQualified": True}
if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
    bid_update_data["selfEligible"] = True

for i in test_bids:
    i.update(bid_update_data)

test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data["procurementMethodType"] = "aboveThresholdUA"
del test_features_tender_ua_data["enquiryPeriod"]
test_features_tender_ua_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_features_tender_ua_data["items"][0]["deliveryDate"] = test_tender_data["items"][0]["deliveryDate"]
test_features_tender_ua_data["items"][0]["deliveryAddress"] = test_tender_data["items"][0]["deliveryAddress"]


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderUAWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    primary_tender_status = "active.tendering"  # status, to which tender should be switched from 'draft'
    question_claim_block_status = (
        "active.auction"
    )  # status, tender cannot be switched to while it has questions/complaints related to its lot
    forbidden_document_modification_actions_status = (
        "active.auction"
    )  # status, in which operations with tender documents (adding, updating) are forbidden
    forbidden_question_modification_actions_status = (
        "active.auction"
    )  # status, in which adding/updating tender questions is forbidden
    forbidden_lot_actions_status = (
        "active.auction"
    )  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"
    )  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    forbidden_auction_actions_status = (
        "active.tendering"
    )  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"
    )  # status, in which adding document to tender auction is forbidden

    periods = PERIODS
    tender_class = Tender

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def set_all_awards_complaint_period_end(self):
        now = get_now()
        startDate = (now - timedelta(days=2)).isoformat()
        endDate = (now - timedelta(days=1)).isoformat()
        tender_document = self.db.get(self.tender_id)
        for award in tender_document["awards"]:
            award.update({"complaintPeriod": {"startDate": startDate, "endDate": endDate}})
        self.db.save(tender_document)


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderUAContentWebTest, self).setUp()
        self.create_tender()
