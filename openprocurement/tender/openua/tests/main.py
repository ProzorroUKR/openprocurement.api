# -*- coding: utf-8 -*-

import unittest

from openprocurement.tender.openua.tests import bid, tender


def suite():
    suite.addTest(bid.suite())
    suite.addTest(tender.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
