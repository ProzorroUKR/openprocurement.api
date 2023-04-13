# -*- coding: utf-8 -*-
import unittest
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender import TenderResourceTestMixin
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    invalid_tender_conditions,
    guarantee,
    create_tender_with_inn,
    create_tender_with_inn_before,
    tender_milestones_required,
    patch_tender_lots_none,
    create_tender_central,
    create_tender_central_invalid,
    tender_minimalstep_validation,
    tender_lot_minimalstep_validation,
    patch_tender_minimalstep_validation,
    tender_with_guarantee,
    tender_with_guarantee_multilot,
    activate_bid_guarantee_multilot,
    create_tender_with_earlier_non_required_unit,
    create_tender_with_required_unit,
    patch_not_author,
)

from openprocurement.tender.openua.tests.tender import TenderUAResourceTestMixin
from openprocurement.tender.openua.tests.tender_blanks import (
    tender_with_main_procurement_category,
    tender_finance_milestones,
    create_tender_with_criteria_lcc,
)
from openprocurement.tender.openeu.tests.base import (
    BaseTenderWebTest,
    test_tender_openeu_data,
    test_tender_openeu_lots,
    test_tender_openeu_bids,
)
from openprocurement.tender.openeu.tests.tender_blanks import (
    one_bid_tender,
    unsuccessful_after_prequalification_tender,
    one_qualificated_bid_tender,
    multiple_bidders_tender,
    lost_contract_for_active_award,
    create_tender_invalid,
    create_tender_generated,
    patch_tender,
    invalid_bid_tender_features,
    invalid_bid_tender_lot,
)
from openprocurement.tender.openeu.models import Tender


class TenderTest(BaseTenderWebTest):
    tender_model = Tender
    initial_data = test_tender_openeu_data


class TenderResourceTest(BaseTenderWebTest, TenderResourceTestMixin, TenderUAResourceTestMixin):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_openeu_data
    test_lots_data = test_tender_openeu_lots
    test_bids_data = test_tender_openeu_bids

    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_create_tender_generated = snitch(create_tender_generated)
    test_patch_tender = snitch(patch_tender)
    test_guarantee = snitch(guarantee)
    test_invalid_bid_tender_features = snitch(invalid_bid_tender_features)
    test_invalid_bid_tender_lot = snitch(invalid_bid_tender_lot)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_create_tender_with_inn_before = snitch(create_tender_with_inn_before)
    test_tender_milestones_required = snitch(tender_milestones_required)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_minimalstep_validation = snitch(tender_minimalstep_validation)
    test_tender_lot_minimalstep_validation = snitch(tender_lot_minimalstep_validation)
    test_patch_tender_minimalstep_validation = snitch(patch_tender_minimalstep_validation)
    test_create_tender_with_criteria_lcc = snitch(create_tender_with_criteria_lcc)
    test_create_tender_with_earlier_non_required_unit = snitch(create_tender_with_earlier_non_required_unit)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_patch_not_author = snitch(patch_not_author)


class TenderProcessTest(BaseTenderWebTest):
    docservice = True
    initial_auth = ("Basic", ("broker", ""))
    initial_data = test_tender_openeu_data
    test_bids_data = test_tender_openeu_bids

    test_invalid_tender_conditions = snitch(invalid_tender_conditions)
    test_one_bid_tender = snitch(one_bid_tender)
    test_unsuccessful_after_prequalification_tender = snitch(unsuccessful_after_prequalification_tender)
    test_one_qualificated_bid_tender = snitch(one_qualificated_bid_tender)
    test_multiple_bidders_tender = snitch(multiple_bidders_tender)
    test_lost_contract_for_active_award = snitch(lost_contract_for_active_award)


class TenderGuarantee(BaseTenderWebTest):
    docservice = True
    initial_status = "draft"
    test_lots_data = test_tender_openeu_lots
    test_bids_data = test_tender_openeu_bids

    test_tender_with_guarantee = snitch(tender_with_guarantee)
    test_tender_with_guarantee_multilot = snitch(tender_with_guarantee_multilot)
    test_activate_bid_guarantee_multilot = snitch(activate_bid_guarantee_multilot)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    suite.addTest(unittest.makeSuite(TenderGuarantee))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
