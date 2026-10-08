import unittest
from copy import deepcopy
from datetime import timedelta
from unittest import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import calculate_date, get_now
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.open.tests.above_threshold_ua.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)
from openprocurement.tender.open.tests.simple_defense.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_data,
    test_tender_simpledefense_required_criteria_ids,
)
from openprocurement.tender.open.tests.simple_defense.criterion_blanks import (
    delete_requirement_evidence,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_data
    initial_lots = test_tender_below_lots
    test_lots_data = test_tender_below_lots
    initial_status = "draft"

    required_criteria = test_tender_simpledefense_required_criteria_ids

    @mock.patch(
        "openprocurement.tender.core.procedure.state.tender_details.BaseTenderDetailsMixin.vat_not_included_validation_from",
        calculate_date(get_now(), timedelta(days=-1)),
    )
    def test_create_tender_criteria_with_vat_included(self):
        # simple.defense allows valueAddedTaxIncluded: the criteria endpoint must apply the procedure's own rules
        data = deepcopy(self.initial_data)
        data["value"]["valueAddedTaxIncluded"] = True
        data.pop("lots", None)
        for item in data["items"]:
            item.pop("relatedLot", None)
        for milestone in data.get("milestones") or []:
            milestone.pop("relatedLot", None)
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        tender = response.json["data"]
        self.assertTrue(tender["value"]["valueAddedTaxIncluded"])
        response = self.app.post_json(
            f"/tenders/{tender['id']}/criteria?acc_token={response.json['access']['token']}",
            {"data": deepcopy(test_exclusion_criteria)},
        )
        self.assertEqual(response.status, "201 Created")


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_data
    test_lots_data = test_tender_below_lots
    initial_lots = test_tender_below_lots


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_data
    test_lots_data = test_tender_below_lots
    initial_lots = test_tender_below_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseSimpleDefContentWebTest,
):
    initial_data = test_tender_simpledefense_data
    test_lots_data = test_tender_below_lots
    initial_lots = test_tender_below_lots

    test_delete_requirement_evidence = snitch(delete_requirement_evidence)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
