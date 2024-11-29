import unittest
from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_data,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)

tender_data = deepcopy(test_tender_cfaua_data)
tender_data["status"] = "draft"


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseTenderContentWebTest):
    initial_status = "draft"
    initial_data = tender_data
    test_lots_data = test_tender_below_lots

    required_criteria = {
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
    }
    article_16_criteria_required = True


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_cfaua_data
    test_lots_data = test_tender_below_lots


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_cfaua_data
    test_lots_data = test_tender_below_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_cfaua_data
    test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
