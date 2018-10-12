# -*- coding: utf-8 -*-
import unittest
import mock
from datetime import timedelta

from copy import deepcopy
from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now

from openprocurement.planning.api.tests.base import (
    test_plan_data, BaseWebTest
)
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
    plan_not_found,
    esco_plan,
    cfaua_plan,
    # PlanResourceBeforeBudgetPeriodTest
    create_plan_budget_year,
    patch_plan_budget_year)

test_plan_data_mode_test = test_plan_data.copy()
test_plan_data_mode_test["mode"] = "test"

test_data_with_year = deepcopy(test_plan_data)
test_data_with_year['budget']['year'] = 2018
del test_data_with_year['budget']['period']

class PlanTest(BaseWebTest):
    initial_data = test_plan_data

    test_simple_add_plan = snitch(simple_add_plan)


class AccreditationPlanTest(BaseWebTest):
    initial_data = test_plan_data
    initial_data_mode_test = test_plan_data_mode_test

    test_create_plan_accrediatation = snitch(create_plan_accreditation)


@mock.patch('openprocurement.planning.api.models.BUDGET_PERIOD_FROM', get_now() - timedelta(days=1))
class PlanResourceTest(BaseWebTest):
    initial_data = test_plan_data
    initial_data_with_year = test_data_with_year

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_create_plan_invalid = snitch(create_plan_invalid)
    test_create_plan_generated = snitch(create_plan_generated)
    test_create_plan = snitch(create_plan)
    test_get_plan = snitch(get_plan)
    test_patch_plan = snitch(patch_plan)
    test_plan_not_found = snitch(plan_not_found)
    test_esco_plan = snitch(esco_plan)
    test_cfaua_plan = snitch(cfaua_plan)


@mock.patch('openprocurement.planning.api.models.BUDGET_PERIOD_FROM', get_now() + timedelta(days=1))
class PlanResourceBeforeBudgetPeriodTest(BaseWebTest):
    initial_data = test_plan_data
    initial_data_with_year = test_data_with_year

    test_create_plan_budget_year = snitch(create_plan_budget_year)
    test_patch_plan_budget_year = snitch(patch_plan_budget_year)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PlanResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
