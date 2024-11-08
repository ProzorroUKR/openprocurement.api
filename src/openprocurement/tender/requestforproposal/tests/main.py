import unittest

from openprocurement.tender.requestforproposal.tests import (
    auction,
    award,
    bid,
    document,
    question,
    tender,
)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(auction.suite())
    suite.addTest(award.suite())
    suite.addTest(bid.suite())
    suite.addTest(document.suite())
    suite.addTest(question.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
