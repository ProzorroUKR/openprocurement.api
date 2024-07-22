import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central,
    create_tender_central_invalid,
    create_tender_with_earlier_non_required_unit,
    create_tender_with_required_unit,
    guarantee,
    patch_tender_minimalstep_validation,
    tender_financing_milestones,
    tender_lot_minimalstep_validation,
    tender_milestones_required,
    tender_minimalstep_validation,
)
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUWebTest,
    BaseCompetitiveDialogUAWebTest,
    test_tender_cd_lots,
    test_tender_cd_stage1_bids,
    test_tender_cdeu_data,
    test_tender_cdua_data,
)
from openprocurement.tender.competitivedialogue.tests.stage1.tender_blanks import (
    create_tender_generated_eu,
    create_tender_generated_ua,
    create_tender_invalid_config,
    create_tender_invalid_eu,
    create_tender_invalid_ua,
    multiple_bidders_tender_eu,
    patch_tender,
    patch_tender_1,
    patch_tender_eu_ua,
    patch_tender_lots_none,
    path_complete_tender,
    tender_delivery_milestones,
    tender_features_invalid,
    tender_milestones_sequence_number,
    tender_with_main_procurement_category,
    try_go_to_ready_stage_eu,
    update_status_complete_owner_ua,
)
from openprocurement.tender.open.tests.tender_blanks import tender_finance_milestones
from openprocurement.tender.openua.tests.tender_blanks import empty_listing


class CompetitiveDialogEUResourceTest(BaseCompetitiveDialogEUWebTest, TenderResourceTestMixin):
    """
    Check base work with tender. (crete, get, edit)
    """

    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_cdeu_data
    initial_lots = test_lots_data = test_tender_cd_lots
    initial_bids = test_bids_data = test_tender_cd_stage1_bids

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid_eu)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
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
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)
    test_tender_financing_milestones = snitch(tender_financing_milestones)
    test_tender_milestones_sequence_number = snitch(tender_milestones_sequence_number)


class CompetitiveDialogUAResourceTest(BaseCompetitiveDialogUAWebTest, TenderResourceTestMixin):
    initial_data = test_tender_cdua_data
    initial_lots = test_lots_data = test_tender_cd_lots

    test_empty_listing = snitch(empty_listing)
    test_create_tender_invalid = snitch(create_tender_invalid_ua)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
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
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)
    test_tender_financing_milestones = snitch(tender_financing_milestones)
    test_tender_milestones_sequence_number = snitch(tender_milestones_sequence_number)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogEUResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CompetitiveDialogUAResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
