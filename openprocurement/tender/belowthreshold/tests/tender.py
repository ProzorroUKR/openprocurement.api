# -*- coding: utf-8 -*-
import os
import unittest

from openprocurement.api.tests.base import BaseWebTest, snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_data, BaseTenderWebTest
)
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderResourceTest
    listing,
    get_tender,
    tender_features_invalid,
    tender_not_found,
    dateModified_tender,
    guarantee,
    tender_Administrator_change,
    listing_draft,
    tender_fields,
    listing_changes,
    create_tender_invalid,
    create_tender_generated,
    create_tender_draft,
    tender_features,
    patch_tender_jsonpatch,
    patch_tender,
    required_field_deletion,
    # TenderProcessTest
    one_valid_bid_tender,
    one_invalid_bid_tender,
    first_bid_tender,
    create_tender,
    invalid_tender_conditions,
    lost_contract_for_active_award,
    # TestCoordinatesRegExp
    coordinates_reg_exp,
    # TenderTest
    simple_add_tender,
)


class TenderTest(BaseWebTest):
    initial_data = test_tender_data
    relative_to = os.path.dirname(__file__)

    test_simple_add_tender = snitch(simple_add_tender)


class TestCoordinatesRegExp(unittest.TestCase):

    test_coordinates_reg_exp = snitch(coordinates_reg_exp)


class TenderResourceTest(BaseWebTest):
    initial_data = test_tender_data
    initial_auth = ('Basic', ('broker', ''))
    relative_to = os.path.dirname(__file__)
    test_tender_status = 'active.enquiries'

    test_listing = snitch(listing)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_not_found = snitch(tender_not_found)
    test_dateModified_tender = snitch(dateModified_tender)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_listing_draft = snitch(listing_draft)
    test_listing_changes = snitch(listing_changes)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender = snitch(create_tender)
    test_tender_fields = snitch(tender_fields)
    test_tender_features = snitch(tender_features)
    test_patch_tender_jsonpatch = snitch(patch_tender_jsonpatch)
    test_patch_tender = snitch(patch_tender)
    test_required_field_deletion = snitch(required_field_deletion)


class TenderProcessTest(BaseTenderWebTest):
    initial_auth = ('Basic', ('broker', ''))
    relative_to = os.path.dirname(__file__)

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


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
