# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import BaseWebTest

from openprocurement.tender.openua.tests.base import test_tender_data, BaseTenderUAWebTest
from openprocurement.tender.openua.tests.tender_blanks import (
    # Tender UA Test
    simple_add_tender,
    # TenderUAResourceTest
    empty_listing,
    listing_changes,
    listing_draft,
    listing,
    patch_draft_invalid_json,
    create_tender,
    get_tender,
    tender_features_invalid,
    tender_features,
    patch_tender_ua,
    dateModified_tender,
    tender_not_found,
    guarantee,
    tender_Administrator_change,
    # TenderUAProcessTest
    invalid_tender_conditions,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    one_valid_bid_tender_ua,
    invalid1_and_1draft_bids_tender,
    activate_bid_after_adding_lot,
    first_bid_tender,
    lost_contract_for_active_award,
)


class TenderUATest(BaseWebTest):
    initial_data = test_tender_data
    test_simple_add_tender = snitch(simple_add_tender)


class TenderUAResourceTest(BaseTenderUAWebTest):
    initial_data = test_tender_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_listing_draft = snitch(listing_draft)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender = snitch(create_tender)
    test_patch_draft_invalid_json = snitch(patch_draft_invalid_json)
    test_create_tender = snitch(create_tender)
    test_get_tender = snitch(get_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_features = snitch(tender_features)
    test_patch_tender_ua = snitch(patch_tender_ua)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)


class TenderUAProcessTest(BaseTenderUAWebTest):
    initial_data = test_tender_data

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)
    test_invalid1_and_1draft_bids_tender = snitch(invalid1_and_1draft_bids_tender)
    test_activate_bid_after_adding_lot = snitch(activate_bid_after_adding_lot)
    test_first_bid_tender = snitch(first_bid_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderUAProcessTest))
    suite.addTest(unittest.makeSuite(TenderUAResourceTest))
    suite.addTest(unittest.makeSuite(TenderUATest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
