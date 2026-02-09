import unittest

from openprocurement.api.constants import KIND_PROCUREMENT_METHOD_TYPE_MAPPING
from openprocurement.api.tests.base import snitch
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.tests.base import (
    BaseTenderWebTest,
    test_tender_arma_bids,
    test_tender_arma_data,
    test_tender_arma_lots,
)
from openprocurement.tender.arma.tests.tender_blanks import (
    create_tender_generated,
    create_tender_invalid,
    invalid_bid_tender_lot,
    lost_contract_for_active_award,
    multiple_bidders_tender,
    one_bid_tender,
    one_qualificated_bid_tender,
    patch_tender,
    patch_tender_draft,
    set_buyers_signer_info,
    set_procuring_entity_signer_info,
    unsuccessful_after_prequalification_tender,
)
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_with_inn,
    create_tender_with_required_unit,
    guarantee,
    invalid_tender_conditions,
    patch_not_author,
    patch_tender_lots_none,
)
from openprocurement.tender.open.tests.tender_blanks import tender_finance_milestones
from openprocurement.tender.openua.tests.tender_blanks import (
    create_tender_invalid_config,
    empty_listing,
    patch_tender_period,
    tender_with_main_procurement_category,
)


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_arma_data
    initial_lots = test_lots_data = test_tender_arma_lots
    initial_bids = test_bids_data = test_tender_arma_bids
    allowed_proc_entity_kinds = KIND_PROCUREMENT_METHOD_TYPE_MAPPING[COMPLEX_ASSET_ARMA]

    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_patch_not_author = snitch(patch_not_author)
    test_empty_listing = snitch(empty_listing)
    test_patch_tender_period = snitch(patch_tender_period)
    test_patch_tender_draft = snitch(patch_tender_draft)
    test_set_buyers_signer_info = snitch(set_buyers_signer_info)
    test_set_procuring_entity_signer_info = snitch(set_procuring_entity_signer_info)

    test_set_procuring_entity_contract_owner = None
    test_contract_template_name_set = None
    test_tender_features = None
    test_tender_features_invalid = None


class TenderProcessTest(BaseTenderWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_arma_data
    initial_lots = test_tender_arma_lots
    initial_bids = test_bids_data = test_tender_arma_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderProcessTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
