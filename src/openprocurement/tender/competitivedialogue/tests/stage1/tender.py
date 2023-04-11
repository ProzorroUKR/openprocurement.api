# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    guarantee,
    tender_milestones_required,
    create_tender_central,
    create_tender_central_invalid,
    tender_minimalstep_validation,
    tender_lot_minimalstep_validation,
    patch_tender_minimalstep_validation,
    create_tender_with_earlier_non_required_unit,
    create_tender_with_required_unit,
)

from openprocurement.tender.openua.tests.tender_blanks import (
    empty_listing,
    tender_finance_milestones,
)

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUWebTest,
    BaseCompetitiveDialogUAWebTest,
    test_tender_cd_lots,
    test_tender_cd_stage1_bids,
    test_tender_cdua_data,
    test_tender_cdeu_data,
)
from openprocurement.tender.competitivedialogue.tests.stage1.tender_blanks import (
    patch_tender_eu_ua,
    patch_tender_lots_none,
    path_complete_tender,
    tender_features_invalid,
    create_tender_invalid_eu,
    create_tender_generated_eu,
    patch_tender,
    multiple_bidders_tender_eu,
    try_go_to_ready_stage_eu,
    create_tender_invalid_ua,
    create_tender_generated_ua,
    patch_tender_1,
    update_status_complete_owner_ua,
    tender_with_main_procurement_category,
)


class CompetitiveDialogEUResourceTest(BaseCompetitiveDialogEUWebTest, TenderResourceTestMixin):
    """
      Check base work with tender. (crete, get, edit)
    """
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdeu_data
    test_lots_data = test_tender_cd_lots
    test_bids_data = test_tender_cd_stage1_bids

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid_eu)
    test_create_tender_generated = snitch(create_tender_generated_eu)
    test_path_complete_tender = snitch(path_complete_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_patch_tender = snitch(patch_tender)
    test_patch_tender_eu = snitch(patch_tender_eu_ua)
    test_guarantee = snitch(guarantee)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender_eu)
    test_try_go_to_ready_stage = snitch(try_go_to_ready_stage_eu)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_tender_lot_minimalstep_validation = snitch(tender_lot_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)
    test_create_tender_with_earlier_non_required_unit = snitch(create_tender_with_earlier_non_required_unit)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)


class CompetitiveDialogUAResourceTest(BaseCompetitiveDialogUAWebTest, TenderResourceTestMixin):
    docservice = True
    initial_data = test_tender_cdua_data
    test_lots_data = test_tender_cd_lots

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid_ua)
    test_create_tender_generated = snitch(create_tender_generated_ua)
    test_path_complete_tender = snitch(path_complete_tender)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_patch_tender = snitch(patch_tender_1)
    test_patch_tender_eu = snitch(patch_tender_eu_ua)
    test_guarantee = snitch(guarantee)
    test_update_status_complete_owner_ua = snitch(update_status_complete_owner_ua)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_tender_lot_minimalstep_validation = snitch(tender_lot_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)
    test_create_tender_with_earlier_non_required_unit = snitch(create_tender_with_earlier_non_required_unit)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogUAResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
