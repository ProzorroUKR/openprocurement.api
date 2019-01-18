# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.core.tests.base import BaseWebTest
from openprocurement.tender.core.migration import migrate_data


class MigrateTest(BaseWebTest):

    def setUp(self):
        super(MigrateTest, self).setUp()
        migrate_data(self.app.app.registry)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MigrateTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
