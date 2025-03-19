import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.core.tests.base import test_main_criteria
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openua_data,
    test_tender_openua_required_criteria_ids,
)
from openprocurement.tender.openua.tests.criterion_blanks import (  # RequirementGroup; Requirement; Evidence
    activate_tender,
    create_criteria_rg,
    create_patch_delete_evidences_from_requirement,
    create_requirement_evidence_invalid,
    create_requirement_evidence_valid,
    create_rg_requirement_invalid,
    create_rg_requirement_valid,
    create_tender_criteria_invalid,
    create_tender_criteria_valid,
    criterion_from_market_category,
    criterion_from_market_profile,
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
    put_rg_requirement_valid_value_change,
    tech_feature_criterion,
    validate_requirement_evidence_document,
    validate_rg_requirement_data_schema,
    validate_rg_requirement_strict_rules,
)


class TenderCriteriaBaseTestMixin:
    def setUp(self):
        super().setUp()
        tender = self.get_tender().json["data"]

        criteria_data = deepcopy(test_main_criteria)
        set_tender_criteria(
            criteria_data,
            tender.get("lots", []),
            tender.get("items", []),
        )

        for criterion in criteria_data:
            for rg in criterion["requirementGroups"]:
                for req in rg["requirements"]:
                    req.pop("eligibleEvidences", None)

        response = self.app.post_json(
            "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": criteria_data},
        )
        for criterion in response.json["data"]:
            if criterion["classification"]["id"].startswith(
                "CRITERION.OTHER.SUBJECT_OF_PROCUREMENT.LOCAL_ORIGIN_LEVEL"
            ):
                self.criteria_id = criterion["id"]
                self.rg_id = criterion["requirementGroups"][0]["id"]
                self.requirement_id = criterion["requirementGroups"][0]["requirements"][0]["id"]
            if criterion["classification"]["id"].startswith("CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION"):
                self.exclusion_criteria_id = criterion["id"]
                self.exclusion_rg_id = criterion["requirementGroups"][0]["id"]
                self.exclusion_requirement_id = criterion["requirementGroups"][0]["requirements"][0]["id"]


class TenderCriteriaTestMixin:
    test_create_tender_criteria_valid = snitch(create_tender_criteria_valid)
    test_create_tender_criteria_invalid = snitch(create_tender_criteria_invalid)
    test_patch_tender_criteria_valid = snitch(patch_tender_criteria_valid)
    test_patch_tender_criteria_invalid = snitch(patch_tender_criteria_invalid)
    test_get_tender_criteria = snitch(get_tender_criteria)
    test_activate_tender = snitch(activate_tender)


class TenderCriteriaRGTestMixin(TenderCriteriaBaseTestMixin):
    test_create_criteria_rg_valid = snitch(create_criteria_rg)
    test_patch_criteria_rg = snitch(patch_criteria_rg)
    test_get_criteria_rg = snitch(get_criteria_rg)


class TenderCriteriaRGRequirementTestMixin(TenderCriteriaBaseTestMixin):
    test_create_rg_requirement_valid = snitch(create_rg_requirement_valid)
    test_create_rg_requirement_invalid = snitch(create_rg_requirement_invalid)
    test_patch_rg_requirement = snitch(patch_rg_requirement)
    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)
    test_put_rg_requirement_valid_value_change = snitch(put_rg_requirement_valid_value_change)
    test_put_rg_requirement_invalid = snitch(put_rg_requirement_invalid)
    test_get_rg_requirement = snitch(get_rg_requirement)
    test_validate_rg_requirement_strict_rules = snitch(validate_rg_requirement_strict_rules)
    test_validate_rg_requirement_data_schema = snitch(validate_rg_requirement_data_schema)

    test_requirement_data = {
        "title": "Фізична особа, яка є учасником процедури закупівлі, ",
        "description": "?",
        "dataType": "boolean",
        "expectedValue": True,
    }
    allowed_put_statuses = ["active.tendering"]


class TenderCriteriaRGRequirementEvidenceTestMixin(TenderCriteriaBaseTestMixin):
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


class TenderCriteriaLccTestMixin:
    test_lcc_criterion_valid = snitch(lcc_criterion_valid)
    test_lcc_criterion_invalid = snitch(lcc_criterion_invalid)


class TenderTechFeatureCriteriaTestMixin:
    test_tech_feature_criterion = snitch(tech_feature_criterion)
    test_criterion_from_market_profile = snitch(criterion_from_market_profile)
    test_criterion_from_market_category = snitch(criterion_from_market_category)


class TenderUACriteriaTest(
    TenderCriteriaTestMixin,
    TenderCriteriaLccTestMixin,
    TenderTechFeatureCriteriaTestMixin,
    BaseTenderUAContentWebTest,
):
    initial_data = test_tender_openua_data
    initial_lots = test_tender_below_lots
    initial_status = "draft"

    required_criteria = test_tender_openua_required_criteria_ids
    article_16_criteria_required = True


class TenderUACriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_openua_data
    test_lots_data = test_tender_below_lots


class TenderUACriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_openua_data
    test_lots_data = test_tender_below_lots


class TenderUACriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderUAContentWebTest,
):
    initial_data = test_tender_openua_data
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
