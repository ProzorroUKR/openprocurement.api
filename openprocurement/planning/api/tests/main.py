# -*- coding: utf-8 -*-

import unittest

from openprocurement.planning.api.tests import plan


def suite():
    suite = unittest.TestSuite()
    suite.addTest(plan.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
