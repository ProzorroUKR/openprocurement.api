# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy
from datetime import timedelta

import mock

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.planning.api.tests.base import BasePlanTest, test_plan_data
from openprocurement.planning.api.tests.plan_blanks import (  # PlanTest; AccreditationPlanTest; PlanResourceTest; PlanBudgetBreakdownTest; PlanResourceBeforeBudgetPeriodTest; Plan Buyers
    cfaua_plan,
    concurrent_plan_update,
    create_plan,
    create_plan_accreditation,
    create_plan_budget_year,
    create_plan_generated,
    create_plan_invalid,
    create_plan_invalid_buyers,
    create_plan_invalid_procurement_method_type,
    create_plan_invalid_procuring_entity,
    create_plan_with_breakdown,
    create_plan_with_breakdown_not_required,
    create_plan_with_breakdown_other_title,
    create_plan_with_breakdown_required,
    create_plan_with_buyers,
    create_plan_with_delivery_address,
    create_plan_with_delivery_address_required_fields,
    create_plan_with_delivery_address_validations,
    create_plan_with_profile,
    create_plan_with_two_buyers,
    create_plan_without_buyers,
    empty_listing,
    esco_plan,
    fail_create_plan_with_amounts_sum_greater,
    fail_create_plan_with_breakdown_invalid_title,
    fail_create_plan_with_breakdown_other_title,
    fail_create_plan_with_diff_breakdown_currencies,
    fail_create_plan_without_buyers,
    get_plan,
    listing,
    listing_moves_from_dts,
    patch_plan,
    patch_plan_budget_year,
    patch_plan_item_quantity,
    patch_plan_to_openuadefense,
    patch_plan_to_simpledefense,
    patch_plan_with_breakdown,
    patch_plan_with_token,
    plan_not_found,
    plan_rationale,
    plan_token_invalid,
)

test_plan_data_mode_test = test_plan_data.copy()
test_plan_data_mode_test["mode"] = "test"

test_data_with_year = deepcopy(test_plan_data)
test_data_with_year["budget"]["year"] = 2018
del test_data_with_year["budget"]["period"]


class PlanTest(BasePlanTest):
    initial_data = test_plan_data

    test_concurrent_plan_update = snitch(concurrent_plan_update)


class AccreditationPlanTest(BasePlanTest):
    initial_data = test_plan_data
    initial_data_mode_test = test_plan_data_mode_test

    test_create_plan_accrediatation = snitch(create_plan_accreditation)


class PlanResourceTest(BasePlanTest):
    initial_data = test_plan_data
    initial_data_with_year = test_data_with_year

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_moves_from_dts = snitch(listing_moves_from_dts)
    test_create_plan_invalid = snitch(create_plan_invalid)
    test_create_plan_invalid_procurement_method_type = snitch(create_plan_invalid_procurement_method_type)
    test_create_plan_invalid_procuring_entity = snitch(create_plan_invalid_procuring_entity)
    test_create_plan_invalid_buyers = snitch(create_plan_invalid_buyers)
    test_create_plan_generated = snitch(create_plan_generated)
    test_create_plan = snitch(create_plan)
    test_get_plan = snitch(get_plan)
    test_patch_plan = snitch(patch_plan)
    test_patch_plan_to_simpledefense = snitch(patch_plan_to_simpledefense)
    test_patch_plan_to_openuadefense = snitch(patch_plan_to_openuadefense)
    test_patch_plan_with_token = snitch(patch_plan_with_token)
    test_patch_plan_item_quantity = snitch(patch_plan_item_quantity)
    test_plan_token_invalid = snitch(plan_token_invalid)
    test_plan_not_found = snitch(plan_not_found)
    test_esco_plan = snitch(esco_plan)
    test_cfaua_plan = snitch(cfaua_plan)
    test_plan_rationale = snitch(plan_rationale)


class PlanBudgetBreakdownTest(BasePlanTest):
    initial_data = test_plan_data

    test_create_plan_with_breakdown = snitch(create_plan_with_breakdown)
    test_create_plan_with_breakdown_required = snitch(create_plan_with_breakdown_required)
    test_create_plan_with_breakdown_not_required = snitch(create_plan_with_breakdown_not_required)
    test_patch_plan_with_breakdown = snitch(patch_plan_with_breakdown)
    test_fail_create_plan_with_breakdown_invalid_title = snitch(fail_create_plan_with_breakdown_invalid_title)
    test_create_plan_with_breakdown_other_title = snitch(create_plan_with_breakdown_other_title)
    test_fail_create_plan_with_breakdown_other_title = snitch(fail_create_plan_with_breakdown_other_title)
    test_fail_create_plan_with_diff_breakdown_currencies = snitch(fail_create_plan_with_diff_breakdown_currencies)
    test_fail_create_plan_with_amounts_sum_greater = snitch(fail_create_plan_with_amounts_sum_greater)
    test_create_plan_with_delivery_address = snitch(create_plan_with_delivery_address)
    test_create_plan_with_delivery_address_required_fields = snitch(create_plan_with_delivery_address_required_fields)
    test_create_plan_with_delivery_address_validations = snitch(create_plan_with_delivery_address_validations)
    test_create_plan_with_profile = snitch(create_plan_with_profile)


@mock.patch("openprocurement.planning.api.procedure.models.budget.BUDGET_PERIOD_FROM", get_now() + timedelta(days=1))
class PlanBudgetYearTest(BasePlanTest):
    initial_data = test_plan_data
    initial_data_with_year = test_data_with_year

    test_create_plan_budget_year = snitch(create_plan_budget_year)
    test_patch_plan_budget_year = snitch(patch_plan_budget_year)


@mock.patch(
    "openprocurement.planning.api.procedure.models.plan.PLAN_BUYERS_REQUIRED_FROM", get_now() + timedelta(days=1)
)
class PlanBuyersTestCase(BasePlanTest):
    initial_data = test_plan_data

    test_create_plan_without_buyers = snitch(create_plan_without_buyers)
    test_fail_create_plan_without_buyers = snitch(fail_create_plan_without_buyers)
    test_create_plan_with_buyers = snitch(create_plan_with_buyers)
    test_create_plan_with_two_buyers = snitch(create_plan_with_two_buyers)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PlanResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
