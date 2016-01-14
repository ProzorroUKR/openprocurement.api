# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.openua.tests.base import BaseTenderUAContentWebTest, test_tender_ua_data



def suite():
    suite = unittest.TestSuite()
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
