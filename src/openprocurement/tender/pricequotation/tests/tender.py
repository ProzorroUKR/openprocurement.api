# -*- coding: utf-8 -*-
import os
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest,
    TenderContentWebTest,
    test_tender_data,
    BaseApiWebTest,
)

from openprocurement.tender.pricequotation.tests.tender_blanks import (
    simple_add_tender,

    listing,
    listing_draft,
    listing_changes,

    one_valid_bid_tender,
    one_invalid_bid_tender,
    first_bid_tender,

    create_tender,
    create_tender_draft,
    create_tender_generated,
    create_tender_invalid,
    create_tender_with_inn,

    invalid_tender_conditions,
    patch_tender,
    patch_tender_by_pq_bot,
    tender_owner_can_change_in_draft,
    tender_owner_cannot_change_in_draft,
    required_field_deletion,
    tender_Administrator_change,
    tender_fields,
    lost_contract_for_active_award,
    create_tender_in_not_draft_status,
)
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    guarantee,
    create_tender_with_inn_before,
    tender_milestones_required,
    coordinates_reg_exp,
    get_tender,
    tender_not_found,
    dateModified_tender,
    patch_not_author,
    tender_items_float_quantity,
    patch_tender_jsonpatch,
    tender_funders,
    tender_with_main_procurement_category,
    create_tender_with_inn_before,
    tender_token_invalid,
)

class TenderResourceTestMixin(object):
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_tender_draft = snitch(create_tender_draft)
    test_tender_owner_can_change_in_draft = snitch(tender_owner_can_change_in_draft)
    test_tender_owner_cannot_change_in_draft = snitch(tender_owner_cannot_change_in_draft)
    test_create_tender = snitch(create_tender)
    test_get_tender = snitch(get_tender)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_token_invalid = snitch(tender_token_invalid)
    test_create_tender_in_not_draft_status = snitch(create_tender_in_not_draft_status)


class TenderTest(BaseApiWebTest):
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TestCoordinatesRegExp(unittest.TestCase):

    test_coordinates_reg_exp = snitch(coordinates_reg_exp)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    initial_data = test_tender_data
    initial_auth = ("Basic", ("broker", ""))

    Test_guarantee = snitch(guarantee)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_tender_fields = snitch(tender_fields)
    test_tender_items_float_quantity = snitch(tender_items_float_quantity)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_required_field_deletion = snitch(required_field_deletion)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_create_tender_with_inn_before = snitch(create_tender_with_inn_before)
    test_patch_tender_by_pq_bot = snitch(patch_tender_by_pq_bot)
    test_invalid_tender_conditions = snitch(invalid_tender_conditions)


class TenderProcessTest(TenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_data
    initial_status = 'active.tendering'
    need_tender = True

    test_one_valid_bid_tender = snitch(one_valid_bid_tender)
    test_one_invalid_bid_tender = snitch(one_invalid_bid_tender)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
