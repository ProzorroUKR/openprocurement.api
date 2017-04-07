# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.api.tests.base import BaseWebTest

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderUAProcessTest
    invalid_tender_conditions,
    # TenderUAResourceTest
    listing,
    listing_changes,
    listing_draft,
    create_tender_draft,
    create_tender,
    tender_features,
    get_tender,
    tender_features_invalid,
    dateModified_tender,
    tender_not_found,
    tender_Administrator_change,
)

from openprocurement.tender.openua.tests.tender_blanks import (
    # TenderUAResourceTest
    empty_listing,
    create_tender_generated,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    # TenderUAProcessTest
    first_bid_tender,
    lost_contract_for_active_award
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAWebTest,
    test_tender_data,
)
from openprocurement.tender.openuadefense.tests.tender_blanks import (
    # TenderUATest
    simple_add_tender,
    # TenderUAResourceTest
    create_tender_invalid,
    patch_tender,
    patch_tender_ua,
    # TenderUAProcessTest
    one_valid_bid_tender_ua,
    one_invalid_bid_tender,
)


class TenderUATest(BaseWebTest):

    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TenderUAResourceTest(BaseTenderUAWebTest):
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_tender_status = 'active.tendering'

    initial_data = test_tender_data

    test_empty_listing = snitch(empty_listing)

    test_listing = snitch(listing)

    test_listing_changes = snitch(listing_changes)

    test_listing_draft = snitch(listing_draft)

    test_create_tender_invalid = snitch(create_tender_invalid)

    test_create_tender_generated = snitch(create_tender_generated)

    test_create_tender_draft = snitch(create_tender_draft)

    test_create_tender = snitch(create_tender)

    test_get_tender = snitch(get_tender)

    test_tender_features_invalid = snitch(tender_features_invalid)

    test_tender_features = snitch(tender_features)

    test_patch_tender = snitch(patch_tender)

    test_patch_tender_ua = snitch(patch_tender_ua)

    test_dateModified_tender = snitch(dateModified_tender)

    test_tender_not_found = snitch(tender_not_found)

    test_tender_Administrator_change = snitch(tender_Administrator_change)

    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)

    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)


class TenderUAProcessTest(BaseTenderUAWebTest):
    initial_data = test_tender_data

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)

    test_one_valid_bid_tender_ua = snitch(one_valid_bid_tender_ua)

    test_one_invalid_bid_tender = snitch(one_invalid_bid_tender)

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
