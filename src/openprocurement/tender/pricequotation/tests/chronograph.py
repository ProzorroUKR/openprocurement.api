# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.pricequotation.tests.base import TenderContentWebTest
from openprocurement.tender.pricequotation.tests.chronograph_blanks import (
    switch_to_qualification,
    switch_to_unsuccessful,
)


class TenderChronographResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_qualification = snitch(switch_to_qualification)
    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderChronographResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
