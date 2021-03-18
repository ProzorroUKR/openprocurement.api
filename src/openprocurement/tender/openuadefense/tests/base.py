# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from copy import deepcopy
from mock import patch

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.utils import get_now
from openprocurement.tender.openuadefense.models import Tender
from openprocurement.tender.openuadefense.tests.periods import PERIODS
from openprocurement.tender.openua.tests.base import (
    now,
    test_features_tender_data,
    BaseTenderUAWebTest as BaseTenderWebTest,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_procuring_entity as test_procuringEntity_api,
    test_tender_data as test_tender_data_api,
)
from openprocurement.tender.belowthreshold.tests.base import test_bids as base_test_bids


test_tender_data = test_tender_ua_data = test_tender_data_api.copy()
test_tender_data["procurementMethodType"] = "aboveThresholdUA.defense"
test_procuringEntity = test_procuringEntity_api.copy()
test_procuringEntity["kind"] = "defense"
test_contactPoint = test_procuringEntity_api["contactPoint"].copy()
test_contactPoint["availableLanguage"] = "uk"
test_procuringEntity["contactPoint"] = test_contactPoint
test_procuringEntity["additionalContactPoints"] = [test_contactPoint.copy()]
test_tender_data["procuringEntity"] = test_procuringEntity
del test_tender_data["enquiryPeriod"]
test_tender_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_tender_data["items"] = [
    {
        "description": "футляри до державних нагород",
        "description_en": "Cases for state awards",
        "classification": {"scheme": "ДК021", "id": "44617100-9", "description": "Cartons"},
        "additionalClassifications": [
            {"scheme": "ДКПП", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
        ],
        "unit": {"name": "item", "code": "44617100-9"},
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
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"
test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data["procurementMethodType"] = "aboveThresholdUA.defense"
test_features_tender_ua_data["procuringEntity"] = test_procuringEntity
del test_features_tender_ua_data["enquiryPeriod"]
test_features_tender_ua_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_features_tender_ua_data["items"][0]["deliveryDate"] = test_tender_data["items"][0]["deliveryDate"]
test_features_tender_ua_data["items"][0]["deliveryAddress"] = test_tender_data["items"][0]["deliveryAddress"]

test_bids = deepcopy(base_test_bids)

bid_update_data = {"selfQualified": True, "selfEligible": True}

for i in test_bids:
    i.update(bid_update_data)


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseTenderUAWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None
    forbidden_lot_actions_status = (
        "active.auction"
    )  # status, in which operations with tender lots (adding, updating, deleting) are forbidden

    periods = PERIODS
    tender_class = Tender

    def setUp(self):
        self.pathcer_release_date = patch("openprocurement.tender.core.validation.RELEASE_SIMPLE_DEFENSE_FROM",
                                          get_now() + timedelta(days=1))
        self.pathcer_release_date.start()
        super(BaseTenderUAWebTest, self).setUp()

    def tearDown(self):
        super(BaseTenderUAWebTest, self).tearDown()
        self.pathcer_release_date.stop()

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        a = self.set_status("active.tendering", startend="complaint_end")
        return a


class BaseTenderUAContentWebTest(BaseTenderUAWebTest):
    initial_data = test_tender_data
    initial_status = None
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseTenderUAContentWebTest, self).setUp()
        self.create_tender()
