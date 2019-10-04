# -*- coding: utf-8 -*-

import unittest

from openprocurement.tender.belowthreshold.tests import auction, award, bid, document, tender, question, complaint


def suite():
    suite = unittest.TestSuite()
    suite.addTest(auction.suite())
    suite.addTest(award.suite())
    suite.addTest(bid.suite())
    suite.addTest(complaint.suite())
    suite.addTest(document.suite())
    suite.addTest(question.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
