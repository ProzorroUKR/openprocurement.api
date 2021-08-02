# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from iso8601 import parse_date
from copy import deepcopy
from mock import patch

from openprocurement.api.tests.base import BaseWebTest
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.tender.simpledefense.models import Tender
from openprocurement.tender.simpledefense.tests.periods import PERIODS
from openprocurement.tender.openua.tests.base import (
    now,
    test_features_tender_data,
    BaseTenderUAWebTest as BaseTenderWebTest,
)
from openprocurement.tender.openuadefense.tests.base import (
    test_procuringEntity as test_procuringEntity_api,
    test_tender_data as test_tender_data_api,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_bids as base_test_bids,
    set_tender_multi_buyers,
    test_organization,
)


test_tender_data = test_tender_ua_data = test_tender_data_api.copy()
test_tender_data["procurementMethodType"] = "simple.defense"
test_procuringEntity = test_procuringEntity_api.copy()
test_tender_data["procuringEntity"] = test_procuringEntity

if SANDBOX_MODE:
    test_tender_data["procurementMethodDetails"] = "quick, accelerator=1440"
test_features_tender_ua_data = test_features_tender_data.copy()
test_features_tender_ua_data["procurementMethodType"] = "simple.defense"
test_features_tender_ua_data["procuringEntity"] = test_procuringEntity
del test_features_tender_ua_data["enquiryPeriod"]
test_features_tender_ua_data["tenderPeriod"] = {"endDate": (now + timedelta(days=16)).isoformat()}
test_features_tender_ua_data["items"][0]["deliveryDate"] = test_tender_data["items"][0]["deliveryDate"]
test_features_tender_ua_data["items"][0]["deliveryAddress"] = test_tender_data["items"][0]["deliveryAddress"]

test_bids = deepcopy(base_test_bids)

bid_update_data = {"selfQualified": True, "selfEligible": True}

for i in test_bids:
    i.update(bid_update_data)

test_tender_data_multi_buyers = set_tender_multi_buyers(
    test_tender_data, test_tender_data["items"][0],
    test_organization
)

class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)


class BaseSimpleDefWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_data
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    forbidden_lot_actions_status = (
        "active.auction"
    )  # status, in which operations with tender lots (adding, updating, deleting) are forbidden

    periods = PERIODS
    tender_class = Tender

    def setUp(self):
        self.pathcer_release_date = patch("openprocurement.tender.core.validation.RELEASE_SIMPLE_DEFENSE_FROM",
                                          parse_date("2021-01-01T00:00:00+03:00"))
        self.pathcer_release_date.start()
        super(BaseSimpleDefWebTest, self).setUp()

    def tearDown(self):
        super(BaseSimpleDefWebTest, self).tearDown()
        self.pathcer_release_date.stop()

    def set_enquiry_period_end(self):
        self.set_status("active.tendering", startend="enquiry_end")

    def set_complaint_period_end(self):
        self.set_status("active.tendering", startend="complaint_end")


class BaseSimpleDefContentWebTest(BaseSimpleDefWebTest):
    initial_data = test_tender_data
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None

    def setUp(self):
        super(BaseSimpleDefContentWebTest, self).setUp()
        self.create_tender()
