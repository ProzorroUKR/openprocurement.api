# -*- coding: utf-8 -*-

import unittest

from openprocurement.tender.limited.tests import tender, award, contract, document, cancellation


def suite():
    suite = unittest.TestSuite()
    suite.addTest(tender.suite())
    suite.addTest(award.suite())
    suite.addTest(document.suite())
    suite.addTest(contract.suite())
    suite.addTest(cancellation.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
