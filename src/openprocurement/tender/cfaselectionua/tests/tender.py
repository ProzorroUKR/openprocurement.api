# -*- coding: utf-8 -*-
import os
import unittest

from copy import deepcopy
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import set_tender_lots
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    patch_tender_lots_none,
    tender_milestones_not_required,
    create_tender_central,
    create_tender_central_invalid,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    test_lots,
    test_tender_data,
    test_agreement,
    test_agreement_features,
    BaseTenderWebTest,
    BaseApiWebTest,
)
from openprocurement.tender.cfaselectionua.tests.tender_blanks import (
    # TenderResourceTest
    listing,
    get_tender,
    tender_features_invalid,
    tender_not_found,
    dateModified_tender,
    guarantee,
    tender_Administrator_change,
    patch_not_author,
    listing_draft,
    tender_fields,
    listing_changes,
    create_tender_invalid,
    create_tender_generated,
    create_tender_draft,
    create_tender_with_value,
    tender_features,
    patch_tender_jsonpatch,
    patch_tender,
    patch_tender_bot,
    patch_tender_to_draft_pending,
    required_field_deletion,
    tender_funders,
    # TenderProcessTest
    one_valid_bid_tender,
    one_invalid_bid_tender,
    first_bid_tender,
    create_tender,
    create_tender_from_terminated_agreement,
    create_tender_from_agreement_with_changes,
    create_tender_from_agreement_with_features,
    create_tender_from_agreement_with_features_0_3,
    invalid_tender_conditions,
    lost_contract_for_active_award,
    # TestCoordinatesRegExp
    coordinates_reg_exp,
    # TenderTest
    simple_add_tender,
    create_tender_with_available_language,
    edit_tender_in_active_enquiries,
)


tender_data = deepcopy(test_tender_data)
set_tender_lots(tender_data, test_lots)
test_lots = deepcopy(tender_data["lots"])


class TenderResourceTestMixin(object):
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_listing = snitch(listing)
    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender = snitch(create_tender)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_from_terminated_agreement = snitch(create_tender_from_terminated_agreement)
    test_create_tender_from_agreement_with_changes = snitch(create_tender_from_agreement_with_changes)
    test_create_tender_from_agreement_with_features = snitch(create_tender_from_agreement_with_features)
    test_create_tender_from_agreement_with_features_0_3 = snitch(create_tender_from_agreement_with_features_0_3)
    test_create_tender_with_value = snitch(create_tender_with_value)
    # test_tender_features = snitch(tender_features)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_patch_not_author = snitch(patch_not_author)
    test_tender_funders = snitch(tender_funders)
    test_patch_tender_bot = snitch(patch_tender_bot)
    test_create_tender_with_available_language = snitch(create_tender_with_available_language)


class TenderTest(BaseApiWebTest):
    initial_data = tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TestCoordinatesRegExp(unittest.TestCase):

    test_coordinates_reg_exp = snitch(coordinates_reg_exp)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    initial_data = tender_data
    primary_tender_status = "draft"
    initial_auth = ("Basic", ("broker", ""))
    initial_agreement = test_agreement
    initial_agreement_with_features = test_agreement_features
    test_lots_data = test_lots

    agreement_id = "11111111111111111111111111111111"

    # test_guarantee = snitch(guarantee)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_tender_fields = snitch(tender_fields)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_required_field_deletion = snitch(required_field_deletion)
    test_patch_tender_to_draft_pending = snitch(patch_tender_to_draft_pending)
    test_edit_tender_in_active_enquiries = snitch(edit_tender_in_active_enquiries)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_milestones_not_required = snitch(tender_milestones_not_required)


class TenderProcessTest(BaseTenderWebTest):
    initial_data = tender_data
    primary_tender_status = "draft"
    initial_auth = ("Basic", ("broker", ""))

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
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
