# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_bids,
    test_organization,
)
from openprocurement.tender.pricequotation.tests.chronograph_blanks import (
    # TenderSwitchTenderingResourceTest
    # TenderSwitchQualificationResourceTest
    switch_to_qualification,
    # TenderSwitchUnsuccessfulResourceTest
    switch_to_unsuccessful,
)
from openprocurement.tender.core.tests.base import change_auth


class TenderSwitchQualificationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_bids[:1]

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderSwitchUnsuccessfulResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
