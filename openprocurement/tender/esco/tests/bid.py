# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.esco.tests.base import (
    test_bids, test_features_tender_data,
    BaseESCOEUContentWebTest
)
from openprocurement.api.tests.base import snitch
from openprocurement.tender.esco.tests.bid_blanks import (
    create_tender_bidder_invalid,
    create_tender_bidder,
    patch_tender_bidder,
    deleted_bid_is_not_restorable,
    bid_Administrator_change,
    bids_activation_on_tender_documents,
    features_bidder_invalid,
    features_bidder
)


class TenderBidResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'
    test_bids_data = test_bids  # TODO: change attribute identificator
    author_data = test_bids_data[0]['tenderers'][0]

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_patch_tender_bidder = snitch(patch_tender_bidder)

    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)


class TenderBidFeaturesResourceTest(BaseESCOEUContentWebTest):
    initial_status = 'active.tendering'
    initial_data = test_features_tender_data
    test_bids_data = test_bids  # TODO: change attribute identificator

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TenderBidResourceTest)
    suite.addTest(TenderBidFeaturesResourceTest)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
