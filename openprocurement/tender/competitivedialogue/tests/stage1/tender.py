# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # CompetitiveDialogResourceTest
    guarantee,
)

from openprocurement.tender.openua.tests.tender_blanks import (
    # CompetitiveDialogResourceTest
    empty_listing
)

from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_data_ua,
    test_tender_data_eu,
    BaseCompetitiveDialogEUWebTest,
    BaseCompetitiveDialogUAWebTest,
    BaseCompetitiveDialogWebTest
)
from openprocurement.tender.competitivedialogue.tests.stage1.tender_blanks import (
    # CompetitiveDialogTest
    simple_add_tender_ua,
    simple_add_tender_eu,
    # CompetitiveDialogResourceTest
    patch_tender_eu_ua,
    path_complete_tender,
    tender_features_invalid,
    # CompetitiveDialogEUResourceTest
    create_tender_invalid_eu,
    create_tender_generated_eu,
    patch_tender,
    multiple_bidders_tender_eu,
    try_go_to_ready_stage_eu,
    # CompetitiveDialogUAResourceTest
    create_tender_invalid_ua,
    create_tender_generated_ua,
    patch_tender_1,
    update_status_complete_owner_ua
)


class CompetitiveDialogTest(BaseCompetitiveDialogWebTest):
    test_tender_data_ua = test_tender_data_ua  # TODO: change attribute identifier
    test_tender_data_eu = test_tender_data_eu  # TODO: change attribute identifier

    test_simple_add_tender_ua = snitch(simple_add_tender_ua)
    test_simple_add_tender_eu = snitch(simple_add_tender_eu)


class CompetitiveDialogEUResourceTest(BaseCompetitiveDialogEUWebTest, TenderResourceTestMixin):
    """
      Check base work with tender. (crete, get, edit)
    """

    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data_eu  # TODO: change attribute identifier

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid_eu)
    test_create_tender_generated = snitch(create_tender_generated_eu)
    test_path_complete_tender = snitch(path_complete_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_patch_tender = snitch(patch_tender)
    test_patch_tender_eu = snitch(patch_tender_eu_ua)
    test_guarantee = snitch(guarantee)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender_eu)
    test_try_go_to_ready_stage = snitch(try_go_to_ready_stage_eu)


class CompetitiveDialogUAResourceTest(BaseCompetitiveDialogUAWebTest, TenderResourceTestMixin):
    initial_data = test_tender_data_ua  # TODO: change attribute identifier

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid_ua)
    test_create_tender_generated = snitch(create_tender_generated_ua)
    test_path_complete_tender = snitch(path_complete_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_patch_tender = snitch(patch_tender_1)
    test_patch_tender_eu = snitch(patch_tender_eu_ua)
    test_guarantee = snitch(guarantee)
    test_update_status_complete_owner_ua = snitch(update_status_complete_owner_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
