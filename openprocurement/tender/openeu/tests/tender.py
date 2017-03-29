# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.base import (
    test_tender_data,
    BaseTenderWebTest,
    test_lots
)
from openprocurement.tender.openeu.tests.tender_blanks import (
    #TenderProcessTest
    invalid_tender_conditions,
    one_bid_tender,
    unsuccessful_after_prequalification_tender,
    one_qualificated_bid_tender,
    multiple_bidders_tender,
    lost_contract_for_active_award,
    #TenderResourceTest
    empty_listing,
    listing,
    listing_changes,
    listing_draft,
    create_tender_invalid,
    create_tender_generated,
    create_tender_draft,
    create_tender,
    get_tender,
    tender_features_invalid,
    tender_features,
    patch_tender,
    patch_tender_eu,
    dateModified_tender,
    tender_not_found,
    guarantee,
    tender_Administrator_change,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    #TenderTest
    simple_add_tender,
)

class TenderTest(BaseTenderWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TenderResourceTest(BaseTenderWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    test_lots_data = test_lots  # TODO: change attribute identifier

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
    test_patch_tender_eu = snitch(patch_tender_eu)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)


class TenderProcessTest(BaseTenderWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data

    test_invalid_tender_conditions = snitch(invalid_bid_tender_features)
    test_one_bid_tender = snitch(invalid_tender_conditions)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
