import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import TenderContentWebTest
from openprocurement.tender.pricequotation.tests.chronograph_blanks import (
    ensure_no_auction_period,
    switch_to_qualification,
    switch_to_unsuccessful,
)
from openprocurement.tender.pricequotation.tests.data import test_tender_pq_bids


class TenderChronographResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_pq_bids

    test_switch_to_qualification = snitch(switch_to_qualification)
    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)
    test_ensure_no_auction_period = snitch(ensure_no_auction_period)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderChronographResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
