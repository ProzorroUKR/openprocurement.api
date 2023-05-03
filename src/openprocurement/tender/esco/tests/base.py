# -*- coding: utf-8 -*-
import os
from copy import deepcopy

from openprocurement.api.context import get_now
from openprocurement.tender.esco.models import Tender
from openprocurement.tender.esco.tests.utils import prepare_items
from openprocurement.tender.openeu.tests.base import (
    BaseTenderWebTest,
    test_tender_openeu_data,
    test_tender_openeu_features_data,
    test_tender_openeu_lots,
    test_tender_openeu_bids,
)

NBU_DISCOUNT_RATE = 0.22

test_tender_esco_data = deepcopy(test_tender_openeu_data)
test_tender_esco_data["procurementMethodType"] = "esco"
test_tender_esco_data["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_esco_data["minimalStepPercentage"] = 0.02712
test_tender_esco_data["fundingKind"] = "other"
test_tender_esco_data["yearlyPaymentsPercentageRange"] = 0.80000

del test_tender_esco_data["value"]
del test_tender_esco_data["minimalStep"]
prepare_items(test_tender_esco_data)


test_tender_esco_features_data = deepcopy(test_tender_openeu_features_data)
test_tender_esco_features_data["procurementMethodType"] = "esco"
test_tender_esco_features_data["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_esco_features_data["minimalStepPercentage"] = 0.027
test_tender_esco_features_data["fundingKind"] = "other"
test_tender_esco_features_data["yearlyPaymentsPercentageRange"] = 0.80000
test_tender_esco_features_data["features"][0]["enum"][0]["value"] = 0.03
test_tender_esco_features_data["features"][0]["enum"][1]["value"] = 0.07
test_tender_esco_features_data["features"][1]["enum"][0]["value"] = 0.03
test_tender_esco_features_data["features"][1]["enum"][1]["value"] = 0.05
test_tender_esco_features_data["features"][1]["enum"][2]["value"] = 0.07

del test_tender_esco_features_data["value"]
del test_tender_esco_features_data["minimalStep"]
prepare_items(test_tender_esco_features_data)

test_tender_esco_lots = deepcopy(test_tender_openeu_lots)
del test_tender_esco_lots[0]["value"]
del test_tender_esco_lots[0]["minimalStep"]
test_tender_esco_lots[0]["minimalStepPercentage"] = 0.02514
# test_lots[0]["fundingKind"] = "other"
test_tender_esco_lots[0]["yearlyPaymentsPercentageRange"] = 0.80000

test_tender_esco_bids = deepcopy(test_tender_openeu_bids)
for bid in test_tender_esco_bids:
    bid["value"] = {
        "yearlyPaymentsPercentage": 0.9,
        "annualCostsReduction": [100] * 21,
        "contractDuration": {"years": 10, "days": 10},
    }

test_tender_esco_config = {
    "hasAuction": True,
}


class BaseESCOWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_esco_data
    initial_config = test_tender_esco_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_auth = ("Basic", ("broker", ""))
    docservice = True

    tender_class = Tender

    # def time_shift(self, *args, **kwargs):
    #     kwargs["extra"] = extra = kwargs.get("extra") or {}
    #     extra["noticePublicationDate"] = get_now().isoformat()
    #     super().time_shift(*args, **kwargs)

    def set_status(self, status, extra=None, startend="start"):
        extra = extra or {}
        extra["noticePublicationDate"] = get_now().isoformat()
        return super().set_status(status, extra, startend)


class BaseESCOContentWebTest(BaseESCOWebTest):
    """ ESCO Content Test """

    initialize_initial_data = True
    initial_status = "active.tendering"

    def setUp(self):
        super(BaseESCOContentWebTest, self).setUp()
        if self.initial_data and self.initialize_initial_data:
            self.create_tender()
