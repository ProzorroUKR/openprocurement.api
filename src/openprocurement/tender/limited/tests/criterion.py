import unittest
from copy import deepcopy
from openprocurement.api.tests.base import snitch

from openprocurement.tender.core.tests.mock import patch_market_product, patch_market_category
from openprocurement.tender.core.tests.utils import set_tender_criteria
from openprocurement.tender.limited.tests.base import (
    test_tender_negotiation_data,
    test_tender_reporting_data,
    test_tender_reporting_config,
    test_lots,
    BaseTenderContentWebTest,
    test_tender_negotiation_config,
)
from openprocurement.tender.limited.tests.criterion_blanks import (
    patch_criteria_rg,
    put_rg_requirement_valid,
    patch_rg_requirement,
    tender_criteria_source_validation,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
)
from openprocurement.tender.core.tests.base import test_localization_criteria
from openprocurement.tender.openua.tests.criterion_blanks import (
    create_criteria_rg,
    get_criteria_rg,
    create_rg_requirement_valid,
    create_rg_requirement_invalid,
    put_rg_requirement_valid_value_change,
    put_rg_requirement_invalid,
    get_rg_requirement,
    validate_rg_requirement_strict_rules,
    validate_rg_requirement_expected_items_not_zero,
)


class TenderCriteriaBaseTestMixin:
    required_criteria = []

    def setUp(self):
        super().setUp()
        tender = self.get_tender().json["data"]
        related_product_id = "foo"
        related_category_id = "bar"
        tender_document = self.mongodb.tenders.get(self.tender_id)
        tender_document["items"][0]["category"] = related_category_id
        tender_document["items"][0]["product"] = related_product_id
        self.mongodb.tenders.save(tender_document)

        criteria_data = deepcopy(test_localization_criteria)
        criteria_data[0]["source"] = "procuringEntity"
        set_tender_criteria(
            criteria_data,
            tender.get("lots", []),
            tender.get("items", []),
        )

        self.product = {"id": related_product_id, "relatedCategory": related_category_id}
        self.category = {
            "id": related_category_id,
            "classification": tender["items"][0]["classification"],
        }
        with patch_market_product(self.product), patch_market_category(self.category):
            response = self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
                {"data": criteria_data},
            )
            criterion = response.json["data"][0]
            self.criteria_id = criterion["id"]
            self.rg_id = criterion["requirementGroups"][0]["id"]
            self.requirement_id = criterion["requirementGroups"][0]["requirements"][0]["id"]


class NegotiationTenderCriteriaTest(TenderCriteriaTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    initial_lots = test_lots_data = test_lots
    initial_config = test_tender_negotiation_config
    initial_status = "draft"
    required_criteria = []

    test_tender_criteria_source_validation = snitch(tender_criteria_source_validation)


class ReportingTenderCriteriaTest(TenderCriteriaTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_reporting_data
    initial_config = test_tender_reporting_config
    initial_status = "draft"
    required_criteria = []

    test_tender_criteria_source_validation = snitch(tender_criteria_source_validation)


class TenderCriteriaRGTest(TenderCriteriaBaseTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    initial_lots = test_lots_data = test_lots
    initial_config = test_tender_negotiation_config
    initial_status = "draft"

    test_create_criteria_rg_valid = snitch(create_criteria_rg)
    test_patch_criteria_rg = snitch(patch_criteria_rg)
    test_get_criteria_rg = snitch(get_criteria_rg)


class TenderCriteriaRGRequirementTest(TenderCriteriaBaseTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_negotiation_data
    initial_lots = test_lots_data = test_lots
    initial_config = test_tender_negotiation_config
    initial_status = "active"
    allowed_put_statuses = ["active"]

    test_create_rg_requirement_valid = snitch(create_rg_requirement_valid)
    test_create_rg_requirement_invalid = snitch(create_rg_requirement_invalid)
    test_patch_rg_requirement = snitch(patch_rg_requirement)
    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)
    test_put_rg_requirement_valid_value_change = snitch(put_rg_requirement_valid_value_change)
    test_put_rg_requirement_invalid = snitch(put_rg_requirement_invalid)
    test_get_rg_requirement = snitch(get_rg_requirement)
    test_validate_rg_requirement_strict_rules = snitch(validate_rg_requirement_strict_rules)
    test_validate_rg_requirement_expected_items_not_zero = snitch(validate_rg_requirement_expected_items_not_zero)

    test_requirement_data = {
        "title": "Фізична особа, яка є учасником процедури закупівлі, ",
        "description": "?",
        "dataType": "boolean",
        "expectedValue": True,
    }


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(NegotiationTenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(ReportingTenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
