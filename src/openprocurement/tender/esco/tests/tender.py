import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (  # TenderProcessTest; TenderResourceTest
    create_tender_central,
    create_tender_central_invalid,
    create_tender_config_test,
    guarantee,
    invalid_tender_conditions,
    patch_items_related_buyer_id,
    patch_tender_lots_none,
    tender_milestones_not_required,
)
from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    BaseESCOWebTest,
    test_tender_esco_bids,
    test_tender_esco_data,
    test_tender_esco_lots,
)
from openprocurement.tender.esco.tests.tender_blanks import (  # TenderESCOTest; TestTenderEU
    create_tender_generated,
    create_tender_invalid,
    create_tender_invalid_config,
    invalid_bid_tender_features,
    patch_tender,
    patch_tender_draft,
    tender_features,
    tender_features_invalid,
    tender_fields,
    tender_fundingKind_default,
    tender_min_value,
    tender_minimal_step_invalid,
    tender_noticePublicationDate,
    tender_value,
    tender_with_nbu_discount_rate,
    tender_yearlyPaymentsPercentageRange,
    tender_yearlyPaymentsPercentageRange_invalid,
)
from openprocurement.tender.openeu.constants import TENDERING_DAYS
from openprocurement.tender.openeu.tests.tender_blanks import (  # TenderProcessTest; TenderResourceTest
    invalid_bid_tender_lot,
    lost_contract_for_active_award,
    multiple_bidders_tender,
    one_bid_tender,
    one_qualificated_bid_tender,
    unsuccessful_after_prequalification_tender,
)
from openprocurement.tender.openua.tests.tender import TenderUAResourceTestMixin
from openprocurement.tender.openua.tests.tender_blanks import (
    tender_finance_milestones,
    tender_with_main_procurement_category,
)


class TenderESCOTest(BaseESCOWebTest):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_esco_data
    test_bids_data = test_tender_esco_bids
    initial_lots = test_tender_esco_lots

    test_tender_value = snitch(tender_value)
    test_tender_min_value = snitch(tender_min_value)
    test_tender_minimal_step_invalid = snitch(tender_minimal_step_invalid)
    test_tender_yearlyPaymentsPercentageRange_invalid = snitch(tender_yearlyPaymentsPercentageRange_invalid)
    test_tender_yearlyPaymentsPercentageRange = snitch(tender_yearlyPaymentsPercentageRange)
    test_tender_fundingKind_default = snitch(tender_fundingKind_default)
    test_tender_noticePublicationDate = snitch(tender_noticePublicationDate)
    test_tender_milestones_not_required = snitch(tender_milestones_not_required)


class TestTenderEU(BaseESCOContentWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):
    """ESCO tender test"""

    docservice = True
    initialize_initial_data = False
    initial_data = test_tender_esco_data
    # for passing test from TenderUAResourceTestMixin
    initial_data["minValue"] = {"amount": 0}
    initial_lots = test_lots_data = test_tender_esco_lots
    initial_bids = test_bids_data = test_tender_esco_bids
    tender_period_duration = TENDERING_DAYS

    test_tender_fields = snitch(tender_fields)
    test_tender_with_nbu_discount_rate = snitch(tender_with_nbu_discount_rate)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_tender_features = snitch(tender_features)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_patch_items_related_buyer_id = snitch(patch_items_related_buyer_id)
    test_create_tender_config_test = snitch(create_tender_config_test)
    test_patch_tender_draft = snitch(patch_tender_draft)


class TestTenderEUProcess(BaseESCOContentWebTest):
    docservice = True
    initialize_initial_data = False
    initial_data = test_tender_esco_data
    initial_bids = test_bids_data = test_tender_esco_bids
    initial_lots = test_tender_esco_lots

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderESCOTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestTenderEU))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestTenderEUProcess))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
