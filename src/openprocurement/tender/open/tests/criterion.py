import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.core.tests.base import test_exclusion_criteria
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_data,
)
from openprocurement.tender.open.tests.criterion_blanks import (
    activate_tender,
    create_criteria_rg,
    create_patch_delete_evidences_from_requirement,
    create_requirement_evidence_invalid,
    create_requirement_evidence_valid,
    create_rg_requirement_invalid,
    create_rg_requirement_valid,
    create_tender_criteria_invalid,
    create_tender_criteria_valid,
    delete_requirement_evidence,
    get_criteria_rg,
    get_requirement_evidence,
    get_rg_requirement,
    get_tender_criteria,
    lcc_criterion_invalid,
    lcc_criterion_valid,
    patch_criteria_rg,
    patch_requirement_evidence,
    patch_rg_requirement,
    patch_tender_criteria_invalid,
    patch_tender_criteria_valid,
    put_rg_requirement_invalid,
    put_rg_requirement_valid,
    validate_requirement_evidence_document,
)


class TenderCriteriaTestMixin:
    test_create_tender_criteria_valid = snitch(create_tender_criteria_valid)
    test_create_tender_criteria_invalid = snitch(create_tender_criteria_invalid)
    test_patch_tender_criteria_valid = snitch(patch_tender_criteria_valid)
    test_patch_tender_criteria_invalid = snitch(patch_tender_criteria_invalid)
    test_get_tender_criteria = snitch(get_tender_criteria)
    test_activate_tender = snitch(activate_tender)


class TenderCriteriaRGTestMixin:
    test_create_criteria_rg_valid = snitch(create_criteria_rg)
    test_patch_criteria_rg = snitch(patch_criteria_rg)
    test_get_criteria_rg = snitch(get_criteria_rg)

    def setUp(self):
        super().setUp()
        criteria_data = deepcopy(test_exclusion_criteria)
        criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": criteria_data},
        )
        self.criteria_id = response.json["data"][0]["id"]


class TenderCriteriaRGRequirementTestMixin:
    test_create_rg_requirement_valid = snitch(create_rg_requirement_valid)
    test_create_rg_requirement_invalid = snitch(create_rg_requirement_invalid)
    test_patch_rg_requirement = snitch(patch_rg_requirement)
    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)
    test_put_rg_requirement_invalid = snitch(put_rg_requirement_invalid)
    test_get_rg_requirement = snitch(get_rg_requirement)

    test_requirement_data = {
        "title": "Фізична особа, яка є учасником процедури закупівлі, ",
        "description": "?",
        "dataType": "boolean",
        "expectedValue": True,
    }
    allowed_put_statuses = ["active.tendering"]

    def setUp(self):
        super().setUp()
        criteria_data = deepcopy(test_exclusion_criteria)
        criteria_data[0]["classification"]["id"] = "CRITERION.OTHER"

        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": criteria_data},
        )
        self.criteria_id = response.json["data"][0]["id"]
        self.rg_id = response.json["data"][0]["requirementGroups"][0]["id"]

        self.exclusion_criteria_id = response.json["data"][1]["id"]
        self.exclusion_rg_id = response.json["data"][1]["requirementGroups"][0]["id"]


class TenderCriteriaRGRequirementEvidenceTestMixin:
    test_create_requirement_evidence_valid = snitch(create_requirement_evidence_valid)
    test_create_requirement_evidence_invalid = snitch(create_requirement_evidence_invalid)
    test_patch_requirement_evidence = snitch(patch_requirement_evidence)
    test_get_requirement_evidence = snitch(get_requirement_evidence)
    test_delete_requirement_evidence = snitch(delete_requirement_evidence)
    test_validate_requirement_evidence_document = snitch(validate_requirement_evidence_document)
    test_create_patch_delete_evidences_from_requirement = snitch(create_patch_delete_evidences_from_requirement)

    test_evidence_data = {
        "title": "Документальне підтвердження",
        "description": "Довідка в довільній формі",
        "type": "document",
    }

    def setUp(self):
        super().setUp()
        criteria_data = deepcopy(test_exclusion_criteria)
        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": criteria_data},
        )
        self.criteria_id = response.json["data"][0]["id"]
        self.rg_id = response.json["data"][0]["requirementGroups"][0]["id"]
        self.requirement_id = response.json["data"][0]["requirementGroups"][0]["requirements"][0]["id"]

        self.exclusion_criteria_id = response.json["data"][0]["id"]
        self.exclusion_rg_id = response.json["data"][0]["requirementGroups"][0]["id"]
        self.exclusion_requirement_id = response.json["data"][0]["requirementGroups"][0]["requirements"][0]["id"]


class TenderUACriteriaTest(TenderCriteriaTestMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    initial_status = "draft"

    required_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
        "CRITERION.OTHER.BID.LANGUAGE",
    }


class TenderUACriteriaLccTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    initial_lots = test_tender_below_lots
    initial_status = "draft"

    def setUp(self):
        self.initial_data = deepcopy(self.initial_data)
        self.initial_data["awardCriteria"] = "lifeCycleCost"
        super().setUp()

    test_lcc_criterion_valid = snitch(lcc_criterion_valid)
    test_lcc_criterion_invalid = snitch(lcc_criterion_invalid)


class TenderUACriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    test_lots_data = test_tender_below_lots


class TenderUACriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    test_lots_data = test_tender_below_lots


class TenderUACriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderUAContentWebTest,
):
    initial_data = test_tender_open_data
    test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderUACriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderUACriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderUACriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderUACriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
