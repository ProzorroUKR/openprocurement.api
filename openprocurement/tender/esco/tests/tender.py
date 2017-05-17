# -*- coding: utf-8 -*-
import unittest
from openprocurement.tender.openeu.constants import TENDERING_DAYS
from openprocurement.tender.esco.tests.base import (
    test_tender_data,
    BaseESCOWebTest, BaseESCOEUContentWebTest,
)
from openprocurement.api.tests.base import snitch

from openprocurement.tender.esco.tests.tender_blanks import (
    simple_add_tender,
    tender_value,
    tender_min_value,
    tender_with_nbu_discount_rate,
)
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    listing, listing_changes, listing_draft,
    create_tender, get_tender,
    dateModified_tender, tender_not_found,
    guarantee, tender_Administrator_change,
)
from openprocurement.tender.openeu.tests.tender_blanks import patch_tender


class TenderESCOEUTest(BaseESCOWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)
    test_tender_value = snitch(tender_value)
    test_tender_min_value = snitch(tender_min_value)


class TestTenderEU(BaseESCOEUContentWebTest):
    """ ESCO EU tender test """
    initialize_initial_data = False
    initial_data = test_tender_data
    tender_period_duration = TENDERING_DAYS

    test_listing = snitch(listing)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender = snitch(create_tender)
    test_tender_with_nbu_discount_rate = snitch(tender_with_nbu_discount_rate)
    test_get_tender = snitch(get_tender)
    test_patch_tender = snitch(patch_tender)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_guarantee = snitch(guarantee)
    test_tender_Administrator_change = snitch(tender_Administrator_change)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderESCOEUTest))
    suite.addTest(unittest.makeSuite(TestTenderEU))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
