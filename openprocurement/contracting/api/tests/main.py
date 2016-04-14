# -*- coding: utf-8 -*-

import unittest

from openprocurement.contracting.api.tests import contract


def suite():
    suite = unittest.TestSuite()
    suite.addTest(contract.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
