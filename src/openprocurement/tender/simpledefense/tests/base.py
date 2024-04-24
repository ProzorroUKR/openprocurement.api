import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_bids,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_multi_buyers
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAWebTest as BaseTenderWebTest,
)
from openprocurement.tender.openua.tests.base import (
    now,
    test_tender_below_features_data,
)
from openprocurement.tender.openuadefense.tests.base import (
    test_tender_openuadefense_data,
    test_tender_openuadefense_procuring_entity,
)
from openprocurement.tender.simpledefense.tests.periods import PERIODS

test_tender_simpledefense_data = test_tender_openuadefense_data.copy()
test_tender_simpledefense_data["procurementMethodType"] = "simple.defense"
test_tender_simpledefense_procuring_entity = test_tender_openuadefense_procuring_entity.copy()
test_tender_simpledefense_data["procuringEntity"] = test_tender_simpledefense_procuring_entity

if SANDBOX_MODE:
    test_tender_simpledefense_data["procurementMethodDetails"] = "quick, accelerator=1440"
test_tender_simpledefense_features_data = test_tender_below_features_data.copy()
test_tender_simpledefense_features_data["procurementMethodType"] = "simple.defense"
test_tender_simpledefense_features_data["procuringEntity"] = test_tender_simpledefense_procuring_entity
del test_tender_simpledefense_features_data["enquiryPeriod"]
test_tender_simpledefense_features_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_simpledefense_features_data["items"][0]["deliveryDate"] = test_tender_simpledefense_data["items"][0][
    "deliveryDate"
]
test_tender_simpledefense_features_data["items"][0]["deliveryAddress"] = test_tender_simpledefense_data["items"][0][
    "deliveryAddress"
]

test_tender_simpledefense_bids = deepcopy(test_tender_below_bids)
for bid in test_tender_simpledefense_bids:
    bid["selfQualified"] = True
    bid["selfEligible"] = True

test_tender_simpledefense_multi_buyers_data = set_tender_multi_buyers(
    test_tender_simpledefense_data, test_tender_simpledefense_data["items"][0], test_tender_below_organization
)

test_tender_simpledefense_config = {
    "hasAuction": True,
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": False,
    "minBidsNumber": 1,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "restricted": False,
    "tenderComplainRegulation": 2,
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseSimpleDefWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_simpledefense_data
    initial_config = test_tender_simpledefense_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    forbidden_lot_actions_status = (
        "active.auction"  # status, in which operations with tender lots (adding, updating, deleting) are forbidden
    )

    periods = PERIODS

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")


class BaseSimpleDefContentWebTest(BaseSimpleDefWebTest):
    initial_data = test_tender_simpledefense_data
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
