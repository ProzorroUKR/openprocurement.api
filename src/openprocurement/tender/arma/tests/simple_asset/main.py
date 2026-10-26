import unittest

from openprocurement.tender.arma.tests.simple_asset import (
    auction,
    award,
    bid,
    cancellation,
    chronograph,
    contract,
    criterion,
    document,
    lot,
    tender,
)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(auction.suite())
    suite.addTest(award.suite())
    suite.addTest(bid.suite())
    suite.addTest(cancellation.suite())
    suite.addTest(chronograph.suite())
    suite.addTest(contract.suite())
    suite.addTest(criterion.suite())
    suite.addTest(document.suite())
    suite.addTest(lot.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
