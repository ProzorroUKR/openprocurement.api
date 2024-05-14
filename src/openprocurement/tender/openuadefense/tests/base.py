import os
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.tests.base import BaseWebTest
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_bids,
    test_tender_below_data,
    test_tender_below_procuring_entity,
)
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAWebTest as BaseTenderWebTest,
)
from openprocurement.tender.openua.tests.base import (
    now,
    test_tender_below_features_data,
)
from openprocurement.tender.openuadefense.tests.periods import PERIODS

test_tender_openuadefense_data = test_tender_below_data.copy()
test_tender_openuadefense_data["procurementMethodType"] = "aboveThresholdUA.defense"
test_tender_openuadefense_procuring_entity = test_tender_below_procuring_entity.copy()
test_tender_openuadefense_procuring_entity["kind"] = "defense"
test_tender_openuadefense_contact_point = test_tender_below_procuring_entity["contactPoint"].copy()
test_tender_openuadefense_contact_point["availableLanguage"] = "uk"
test_tender_openuadefense_procuring_entity["contactPoint"] = test_tender_openuadefense_contact_point
test_tender_openuadefense_procuring_entity["additionalContactPoints"] = [test_tender_openuadefense_contact_point.copy()]
test_tender_openuadefense_data["procuringEntity"] = test_tender_openuadefense_procuring_entity
del test_tender_openuadefense_data["enquiryPeriod"]
test_tender_openuadefense_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_openuadefense_data["items"] = [
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
    test_tender_openuadefense_data["procurementMethodDetails"] = "quick, accelerator=1440"
test_tender_openuadefense_features_data = test_tender_below_features_data.copy()
test_tender_openuadefense_features_data["procurementMethodType"] = "aboveThresholdUA.defense"
test_tender_openuadefense_features_data["procuringEntity"] = test_tender_openuadefense_procuring_entity
del test_tender_openuadefense_features_data["enquiryPeriod"]
test_tender_openuadefense_features_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_openuadefense_features_data["items"][0]["deliveryDate"] = test_tender_openuadefense_data["items"][0][
    "deliveryDate"
]
test_tender_openuadefense_features_data["items"][0]["deliveryAddress"] = test_tender_openuadefense_data["items"][0][
    "deliveryAddress"
]

test_tender_openuadefense_bids = deepcopy(test_tender_below_bids)
for bid in test_tender_openuadefense_bids:
    bid["selfQualified"] = True
    bid["selfEligible"] = True

test_tender_openuadefense_config = {
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
    "hasValueEstimation": True,
    "hasQualificationComplaints": False,
    "tenderComplainRegulation": 2,
    "qualificationComplainDuration": 0,
    "awardComplainDuration": 4,
    "restricted": False,
    "cancellationComplainDuration": 10,
}


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderUAWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_openuadefense_data
    initial_config = test_tender_openuadefense_config
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
        a = self.set_status("active.tendering", startend="complaint_end")
        return a


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_openuadefense_data
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super().setUp()
        self.create_tender()
