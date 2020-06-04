# -*- coding: utf-8 -*-
import unittest
import mock
from datetime import timedelta

from copy import deepcopy
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.planning.api.tests.base import test_plan_data, BasePlanTest
from openprocurement.planning.api.tests.plan_blanks import (
    # PlanTest
    simple_add_plan,
    # AccreditationPlanTest
    create_plan_accreditation,
    # PlanResourceTest
    empty_listing,
    listing,
    listing_changes,
    create_plan_invalid,
    create_plan_generated,
    create_plan,
    get_plan,
    patch_plan,
    patch_plan_with_token,
    patch_plan_item_quantity,
    plan_token_invalid,
    plan_not_found,
    esco_plan,
    cfaua_plan,
    # PlanBudgetBreakdownTest
    create_plan_with_breakdown,
    patch_plan_with_breakdown,
    fail_create_plan_with_breakdown_invalid_title,
    create_plan_with_breakdown_other_title,
    fail_create_plan_with_breakdown_other_title,
    fail_create_plan_with_diff_breakdown_currencies,
    fail_create_plan_with_amounts_sum_greater,
    # PlanResourceBeforeBudgetPeriodTest
    create_plan_budget_year,
    patch_plan_budget_year,
    # Plan Buyers
    create_plan_without_buyers,
    fail_create_plan_without_buyers,
    create_plan_with_buyers,
    create_plan_with_two_buyers,
    create_plan_with_breakdown_required,
    create_plan_with_breakdown_not_required,
    create_plan_invalid_procuring_entity,
    create_plan_invalid_buyers,
    create_plan_invalid_procurement_method_type,
)

test_plan_data_mode_test = test_plan_data.copy()
test_plan_data_mode_test["mode"] = "test"

test_data_with_year = deepcopy(test_plan_data)
test_data_with_year["budget"]["year"] = 2018
del test_data_with_year["budget"]["period"]


class PlanTest(BasePlanTest):
    initial_data = test_plan_data

    test_simple_add_plan = snitch(simple_add_plan)


class AccreditationPlanTest(BasePlanTest):
    initial_data = test_plan_data
    initial_data_mode_test = test_plan_data_mode_test

    test_create_plan_accrediatation = snitch(create_plan_accreditation)


class PlanResourceTest(BasePlanTest):
    initial_data = test_plan_data
    initial_data_with_year = test_data_with_year

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_create_plan_invalid = snitch(create_plan_invalid)
    test_create_plan_invalid_procurement_method_type = snitch(create_plan_invalid_procurement_method_type)
    test_create_plan_invalid_procuring_entity = snitch(create_plan_invalid_procuring_entity)
    test_create_plan_invalid_buyers = snitch(create_plan_invalid_buyers)
    test_create_plan_generated = snitch(create_plan_generated)
    test_create_plan = snitch(create_plan)
    test_get_plan = snitch(get_plan)
    test_patch_plan = snitch(patch_plan)
    test_patch_plan_with_token = snitch(patch_plan_with_token)
    test_patch_plan_item_quantity = snitch(patch_plan_item_quantity)
    test_plan_token_invalid = snitch(plan_token_invalid)
    test_plan_not_found = snitch(plan_not_found)
    test_esco_plan = snitch(esco_plan)
    test_cfaua_plan = snitch(cfaua_plan)


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


@mock.patch("openprocurement.planning.api.models.BUDGET_PERIOD_FROM", get_now() + timedelta(days=1))
class PlanBudgetYearTest(BasePlanTest):
    initial_data = test_plan_data
    initial_data_with_year = test_data_with_year

    test_create_plan_budget_year = snitch(create_plan_budget_year)
    test_patch_plan_budget_year = snitch(patch_plan_budget_year)


@mock.patch("openprocurement.planning.api.models.PLAN_BUYERS_REQUIRED_FROM", get_now() + timedelta(days=1))
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
