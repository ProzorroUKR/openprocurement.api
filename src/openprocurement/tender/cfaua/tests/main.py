# -*- coding: utf-8 -*-

import unittest
from openprocurement.tender.cfaua.tests import tender


def suite():
    suite = unittest.TestSuite()
    suite.addTest(tender.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
