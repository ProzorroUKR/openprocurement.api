# -*- coding: utf-8 -*-
import os
from copy import deepcopy

from openprocurement.tender.esco.models import Tender
from openprocurement.tender.openeu.tests.base import (
    BaseTenderWebTest,
    test_features_tender_data as base_eu_test_features_data,
    test_tender_data as base_eu_test_data,
    test_lots as base_eu_lots,
    test_bids as base_eu_bids,
)

NBU_DISCOUNT_RATE = 0.22

test_tender_data = deepcopy(base_eu_test_data)
test_tender_data["procurementMethodType"] = "esco"
test_tender_data["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_data["minimalStepPercentage"] = 0.02712
test_tender_data["fundingKind"] = "other"
test_tender_data["yearlyPaymentsPercentageRange"] = 0.80000

del test_tender_data["value"]
del test_tender_data["minimalStep"]

test_features_tender_data = deepcopy(base_eu_test_features_data)
test_features_tender_data["procurementMethodType"] = "esco"
test_features_tender_data["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_features_tender_data["minimalStepPercentage"] = 0.027
test_features_tender_data["fundingKind"] = "other"
test_features_tender_data["yearlyPaymentsPercentageRange"] = 0.80000
test_features_tender_data["features"][0]["enum"][0]["value"] = 0.03
test_features_tender_data["features"][0]["enum"][1]["value"] = 0.07
test_features_tender_data["features"][1]["enum"][0]["value"] = 0.03
test_features_tender_data["features"][1]["enum"][1]["value"] = 0.05
test_features_tender_data["features"][1]["enum"][2]["value"] = 0.07

del test_features_tender_data["value"]
del test_features_tender_data["minimalStep"]

test_lots = deepcopy(base_eu_lots)
del test_lots[0]["value"]
del test_lots[0]["minimalStep"]
test_lots[0]["minimalStepPercentage"] = 0.02514
test_lots[0]["fundingKind"] = "other"
test_lots[0]["yearlyPaymentsPercentageRange"] = 0.80000

test_bids = deepcopy(base_eu_bids)
for bid in test_bids:
    bid["value"] = {
        "yearlyPaymentsPercentage": 0.9,
        "annualCostsReduction": [100] * 21,
        "contractDuration": {"years": 10, "days": 10},
    }


class BaseESCOWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = None
    initial_status = None
    initial_bids = None
    initial_lots = None
    initial_auth = ("Basic", ("broker", ""))
    docservice = False

    tender_class = Tender


class BaseESCOContentWebTest(BaseESCOWebTest):
    """ ESCO Content Test """

    initialize_initial_data = True
    initial_data = test_tender_data

    def setUp(self):
        super(BaseESCOContentWebTest, self).setUp()
        if self.initial_data and self.initialize_initial_data:
            self.create_tender()
