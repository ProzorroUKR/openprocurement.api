import unittest
from copy import deepcopy

from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
    test_tender_cdeu_data,
    test_tender_cdeu_required_criteria_ids,
    test_tender_cdua_data,
    test_tender_cdua_required_criteria_ids,
)
from openprocurement.tender.open.tests.above_threshold_ua.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderCDEUCriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_cdeu_data
    initial_lots = test_tender_below_lots
    initial_status = "draft"

    required_criteria = test_tender_cdeu_required_criteria_ids
    article_16_criteria_required = True


class TenderCDUACriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogUAContentWebTest):
    initial_data = test_tender_cdua_data
    initial_lots = test_tender_below_lots

    def test_create_tender_criteria_without_english_fields(self):
        data = deepcopy(self.initial_data)
        del data["procuringEntity"]["name_en"]
        del data["procuringEntity"]["identifier"]["legalName_en"]
        del data["procuringEntity"]["contactPoint"]["name_en"]
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        tender_id = response.json["data"]["id"]
        tender_token = response.json["access"]["token"]

        response = self.app.post_json(
            f"/tenders/{tender_id}/criteria?acc_token={tender_token}", {"data": deepcopy(test_exclusion_criteria)}
        )
        self.assertEqual(response.status, "201 Created")

    initial_status = "draft"

    required_criteria = test_tender_cdua_required_criteria_ids
    article_16_criteria_required = True


class TenderCDEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_cdeu_data
    test_lots_data = test_tender_below_lots


class TenderCDUACriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogUAContentWebTest):
    initial_data = test_tender_cdua_data
    test_lots_data = test_tender_below_lots


class TenderCDEUCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_cdeu_data
    test_lots_data = test_tender_below_lots


class TenderCDUACriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseCompetitiveDialogUAContentWebTest):
    initial_data = test_tender_cdua_data
    test_lots_data = test_tender_below_lots


class TenderCDEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogEUContentWebTest,
):
    initial_data = test_tender_cdeu_data
    test_lots_data = test_tender_below_lots


class TenderCDUACriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogUAContentWebTest,
):
    initial_data = test_tender_cdua_data
    test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaRGRequirementEvidenceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
