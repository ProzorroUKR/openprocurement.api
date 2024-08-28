import os
from copy import deepcopy
from datetime import datetime, timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    BaseTenderWebTest as BaseBaseTenderWebTest,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_data,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_multi_buyers

now = datetime.now()
test_tender_reporting_data = test_tender_below_data.copy()
del test_tender_reporting_data["enquiryPeriod"]
del test_tender_reporting_data["tenderPeriod"]
del test_tender_reporting_data["minimalStep"]

test_tender_reporting_data["procurementMethodType"] = "reporting"
test_tender_reporting_data["procurementMethodRationale"] = "simple"
test_tender_reporting_data["procuringEntity"]["kind"] = "general"
if SANDBOX_MODE:
    test_tender_reporting_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_negotiation_data = deepcopy(test_tender_reporting_data)
test_tender_negotiation_data["procurementMethodType"] = "negotiation"
test_tender_negotiation_data["cause"] = "twiceUnsuccessful"
test_tender_negotiation_data["causeDescription"] = "chupacabra"
if SANDBOX_MODE:
    test_tender_negotiation_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_negotiation_data_2items = deepcopy(test_tender_negotiation_data)
test_tender_negotiation_data_2items["items"] = [
    deepcopy(test_tender_negotiation_data_2items["items"][0]),
    deepcopy(test_tender_negotiation_data_2items["items"][0]),
]

test_tender_negotiation_quick_data = deepcopy(test_tender_reporting_data)
test_tender_negotiation_quick_data["procurementMethodType"] = "negotiation.quick"
test_tender_negotiation_quick_data["cause"] = "additionalConstruction"
test_tender_negotiation_quick_data["causeDescription"] = "chupacabra"
if SANDBOX_MODE:
    test_tender_negotiation_quick_data["procurementMethodDetails"] = "quick, accelerator=1440"

test_tender_negotiation_quick_data_2items = deepcopy(test_tender_negotiation_quick_data)
test_tender_negotiation_quick_data_2items["items"] = [
    deepcopy(test_tender_negotiation_quick_data_2items["items"][0]),
    deepcopy(test_tender_negotiation_quick_data_2items["items"][0]),
]

test_lots = [
    {"title": "lot title", "description": "lot description", "value": deepcopy(test_tender_negotiation_data["value"])}
]

test_tender_data_multi_buyers = set_tender_multi_buyers(
    test_tender_reporting_data, test_tender_reporting_data["items"][0], test_tender_below_organization
)

test_tender_negotiation_data_multi_buyers = set_tender_multi_buyers(
    test_tender_negotiation_data, test_tender_negotiation_data["items"][0], test_tender_below_organization
)

test_tender_negotiation_quick_data_multi_buyers = set_tender_multi_buyers(
    test_tender_negotiation_quick_data, test_tender_negotiation_quick_data["items"][0], test_tender_below_organization
)

test_tender_reporting_config = {
    "hasAuction": False,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": False,
    "hasAwardComplaints": False,
    "hasCancellationComplaints": False,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 0,
    "cancellationComplainDuration": 0,
    "clarificationUntilDuration": 0,
    "qualificationDuration": 0,
    "restricted": False,
}

test_tender_negotiation_config = {
    "hasAuction": False,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": False,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 10,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 0,
    "qualificationDuration": 0,
    "restricted": False,
}

test_tender_negotiation_quick_config = {
    "hasAuction": False,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": False,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 0,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 5,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 0,
    "qualificationDuration": 0,
    "restricted": False,
}


class BaseTenderWebTest(BaseBaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_reporting_data
    initial_config = test_tender_reporting_config
    initial_status = "active"
    initial_bids = None
    initial_lots = None
    initial_auth = ("Basic", ("broker", ""))
    primary_tender_status = "active"  # status, to which tender should be switched from 'draft'
    forbidden_document_modification_actions_status = (
        "complete"  # status, in which operations with tender documents (adding, updating) are forbidden
    )
    forbidden_contract_document_modification_actions_status = (
        "complete"  # status, in which operations with tender's contract documents (adding, updating) are forbidden
    )

    periods = {}

    def set_all_awards_complaint_period_end(self):
        now = get_now()
        startDate = (now - timedelta(days=2)).isoformat()
        endDate = (now - timedelta(days=1)).isoformat()
        tender_document = self.mongodb.tenders.get(self.tender_id)
        for award in tender_document["awards"]:
            award.update({"complaintPeriod": {"startDate": startDate, "endDate": endDate}})
        self.mongodb.tenders.save(tender_document)


class BaseTenderContentWebTest(BaseTenderWebTest):
    initial_status = "active"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
