# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    #TenderProcessTest
    invalid_tender_conditions,
    #TenderResourceTest
    guarantee,
)

from openprocurement.tender.openua.tests.tender import TenderUAResourceTestMixin

from openprocurement.tender.openeu.tests.base import (
    test_tender_data,
    BaseTenderWebTest,
    test_lots,
    test_bids,
)
from openprocurement.tender.openeu.tests.tender_blanks import (
    #TenderProcessTest
    one_bid_tender,
    unsuccessful_after_prequalification_tender,
    one_qualificated_bid_tender,
    multiple_bidders_tender,
    lost_contract_for_active_award,
    #TenderResourceTest
    create_tender_invalid,
    create_tender_generated,
    patch_tender,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
    #TenderTest
    simple_add_tender,
)


class TenderTest(BaseTenderWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids

    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)


class TenderProcessTest(BaseTenderWebTest):

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    test_bids_data = test_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
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
