# -*- coding: utf-8 -*-

import unittest

from openprocurement.tender.pricequotation.tests import\
    award, bid, document, tender


def suite():
    suite = unittest.TestSuite()
    suite.addTest(award.suite())
    suite.addTest(bid.suite())
    suite.addTest(document.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
