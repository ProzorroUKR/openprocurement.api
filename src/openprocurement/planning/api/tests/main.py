# -*- coding: utf-8 -*-

import unittest

from openprocurement.planning.api.tests import plan, document


def suite():
    suite = unittest.TestSuite()
    suite.addTest(plan.suite())
    suite.addTest(document.suite())
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
