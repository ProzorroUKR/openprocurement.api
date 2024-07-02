import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17, SANDBOX_MODE
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest,
    test_tender_below_bids,
    test_tender_below_data,
    test_tender_below_features_data,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_multi_buyers
from openprocurement.tender.openua.tests.periods import PERIODS

now = get_now()

test_tender_openua_data = test_tender_below_data.copy()
test_tender_openua_data["procurementMethodType"] = "aboveThresholdUA"
del test_tender_openua_data["enquiryPeriod"]
test_tender_openua_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_openua_data["items"] = [
    {
        "description": "футляри до державних нагород",
        "description_en": "Cases for state awards",
        "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
        "additionalClassifications": [
            {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
        ],
        "unit": {"name": "item", "code": "KGM", "value": {"amount": 6}},
        "quantity": 5,
        "deliveryDate": {
            "startDate": (now + timedelta(days=2)).isoformat(),
            "endDate": (now + timedelta(days=5)).isoformat(),
        },
        "deliveryAddress": {
            "countryName": "Україна",
            "postalCode": "79000",
            "region": "м. Київ",
            "locality": "м. Київ",
            "streetAddress": "вул. Банкова 1",
        },
    }
]
if SANDBOX_MODE:
    test_tender_openua_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_openua_bids = deepcopy(test_tender_below_bids)
for bid in test_tender_openua_bids:
    bid["selfQualified"] = True
    if get_now() < RELEASE_ECRITERIA_ARTICLE_17:
        bid["selfEligible"] = True

test_tender_openua_three_bids = deepcopy(test_tender_openua_bids)
test_tender_openua_three_bids.append(
    {
        "tenderers": [test_tender_below_organization],
        "value": {"amount": 489.0, "currency": "UAH", "valueAddedTaxIncluded": True},
        "selfQualified": True,
    }
)

test_tender_openua_features_data = test_tender_below_features_data.copy()
test_tender_openua_features_data["procurementMethodType"] = "aboveThresholdUA"
del test_tender_openua_features_data["enquiryPeriod"]
test_tender_openua_features_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_openua_features_data["items"][0]["deliveryDate"] = test_tender_openua_data["items"][0]["deliveryDate"]
test_tender_openua_features_data["items"][0]["deliveryAddress"] = test_tender_openua_data["items"][0]["deliveryAddress"]


test_tender_openua_multi_buyers_data = set_tender_multi_buyers(
    test_tender_openua_data, test_tender_openua_data["items"][0], test_tender_below_organization
)

test_tender_openua_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 2,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 4,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 10,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 3,
    "restricted": False,
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderUAWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_openua_data
    initial_config = test_tender_openua_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_criteria = None
    min_bids_number = 2
    primary_tender_status = "active.tendering"  # status, to which tender should be switched from 'draft'
    question_claim_block_status = (
        "active.auction"  # status, tender cannot be switched to while it has questions/complaints related to its lot
    )
    forbidden_document_modification_actions_status = (
        "active.auction"  # status, in which operations with tender documents (adding, updating) are forbidden
    )
    forbidden_question_add_actions_status = "active.auction"  # status, in which adding tender questions is forbidden
    forbidden_question_update_actions_status = (
        "active.auction"  # status, in which updating tender questions is forbidden
    )
    forbidden_lot_actions_status = (
        "active.auction"  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    )
    forbidden_contract_document_modification_actions_status = (
        "unsuccessful"  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    )
    forbidden_auction_actions_status = "active.tendering"  # status, in which operations with tender auction (getting auction info, reporting auction results, updating auction urls) and adding tender documents are forbidden
    forbidden_auction_document_create_actions_status = (
        "active.tendering"  # status, in which adding document to tender auction is forbidden
    )

    periods = PERIODS

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")

    def set_all_awards_complaint_period_end(self):
        now = get_now()
        startDate = (now - timedelta(days=2)).isoformat()
        endDate = (now - timedelta(days=1)).isoformat()
        tender_document = self.mongodb.tenders.get(self.tender_id)
        for award in tender_document["awards"]:
            award.update({"complaintPeriod": {"startDate": startDate, "endDate": endDate}})
        self.mongodb.tenders.save(tender_document)


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_openua_data
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
