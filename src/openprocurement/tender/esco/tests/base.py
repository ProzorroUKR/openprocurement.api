import os
from copy import deepcopy

from openprocurement.api.context import get_request_now
from openprocurement.tender.core.tests.base import (
    get_criteria_by_ids,
    test_article_16_criteria,
    test_criteria_all,
)
from openprocurement.tender.esco.tests.utils import prepare_items
from openprocurement.tender.openeu.tests.base import (
    BaseTenderWebTest,
    test_tender_openeu_bids,
    test_tender_openeu_data,
    test_tender_openeu_features_data,
    test_tender_openeu_lots,
)

NBU_DISCOUNT_RATE = 0.22

test_tender_esco_data = deepcopy(test_tender_openeu_data)
del test_tender_esco_data["contractTemplateName"]
test_tender_esco_data["procurementMethodType"] = "esco"
test_tender_esco_data["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_esco_data["fundingKind"] = "other"

del test_tender_esco_data["value"]
prepare_items(test_tender_esco_data)


test_tender_esco_features_data = deepcopy(test_tender_openeu_features_data)
test_tender_esco_features_data["procurementMethodType"] = "esco"
test_tender_esco_features_data["NBUdiscountRate"] = NBU_DISCOUNT_RATE
test_tender_esco_features_data["fundingKind"] = "other"
test_tender_esco_features_data["features"][0]["enum"][0]["value"] = 0.03
test_tender_esco_features_data["features"][0]["enum"][1]["value"] = 0.07
test_tender_esco_features_data["features"][1]["enum"][0]["value"] = 0.03
test_tender_esco_features_data["features"][1]["enum"][1]["value"] = 0.05
test_tender_esco_features_data["features"][1]["enum"][2]["value"] = 0.07

del test_tender_esco_features_data["value"]
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
    "hasAwardingOrder": True,
    "hasValueRestriction": True,
    "valueCurrencyEquality": True,
    "hasPrequalification": True,
    "minBidsNumber": 2,
    "hasPreSelectionAgreement": False,
    "hasTenderComplaints": True,
    "hasAwardComplaints": True,
    "hasCancellationComplaints": True,
    "hasValueEstimation": False,
    "hasQualificationComplaints": True,
    "tenderComplainRegulation": 4,
    "qualificationComplainDuration": 5,
    "awardComplainDuration": 10,
    "cancellationComplainDuration": 10,
    "clarificationUntilDuration": 3,
    "qualificationDuration": 20,
    "restricted": False,
}

test_tender_esco_required_criteria_ids = {
    "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
    "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
    "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
    "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
    "CRITERION.EXCLUSION.CONVICTIONS.TERRORIST_OFFENCES",
    "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.EARLY_TERMINATION",
    "CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES",
    "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
    "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
    "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
    "CRITERION.EXCLUSION.NATIONAL.OTHER",
    "CRITERION.OTHER.BID.LANGUAGE",
    "CRITERION.OTHER.BID.VALIDITY_PERIOD",
    "CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.MANAGEMENT.SUBCONTRACTING_PROPORTION",
}

test_tender_esco_criteria = []
test_tender_esco_criteria.extend(get_criteria_by_ids(test_criteria_all, test_tender_esco_required_criteria_ids))
test_tender_esco_criteria.extend(test_article_16_criteria[:1])


class BaseESCOWebTest(BaseTenderWebTest):
    relative_to = os.path.dirname(__file__)
    initial_data = test_tender_esco_data
    initial_config = test_tender_esco_config
    initial_status = "active.tendering"
    initial_bids = None
    initial_lots = None
    initial_auth = ("Basic", ("broker", ""))

    # def time_shift(self, *args, **kwargs):
    #     kwargs["extra"] = extra = kwargs.get("extra") or {}
    #     extra["noticePublicationDate"] = get_now().isoformat()
    #     super().time_shift(*args, **kwargs)

    def set_status(self, status, extra=None, startend="start"):
        extra = extra or {}
        extra["noticePublicationDate"] = get_request_now().isoformat()
        return super().set_status(status, extra, startend)


class BaseESCOContentWebTest(BaseESCOWebTest):
    """ESCO Content Test"""

    initialize_initial_data = True
    initial_status = "active.tendering"

    def setUp(self):
        super().setUp()
        if self.initial_data and self.initialize_initial_data:
            self.create_tender()
