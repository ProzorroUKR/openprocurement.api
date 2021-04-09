# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.simpledefense.tests.base import test_tender_data, BaseSimpleDefContentWebTest
from openprocurement.tender.simpledefense.tests.criterion_blanks import (
    activate_tender,
    delete_requirement_evidence,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots
    test_lots_data = test_lots
    initial_status = "draft"

    test_activate_tender = snitch(activate_tender)


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_lots = test_lots


class TenderCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseSimpleDefContentWebTest
):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_lots = test_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseSimpleDefContentWebTest,
):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_lots = test_lots

    test_delete_requirement_evidence = snitch(delete_requirement_evidence)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCriteriaTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
