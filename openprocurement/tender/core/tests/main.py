# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.core.tests import tender, models, utils


def suite():
    suite = unittest.TestSuite()
    suite.addTest(tender.suite())
    suite.addTest(models.suite())
    suite.addTest(utils.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
