import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central,
    create_tender_central_invalid,
    create_tender_config_test,
    create_tender_draft,
    create_tender_with_earlier_non_required_unit,
    create_tender_with_inn,
    create_tender_with_required_unit,
    dateModified_tender,
    get_tender,
    listing_draft,
    patch_items_related_buyer_id,
    patch_tender_draft,
    patch_tender_lots_none,
    tender_delivery_milestones,
    tender_funders,
    tender_milestones_not_required,
    tender_milestones_required,
    tender_not_found,
)
from openprocurement.tender.competitivedialogue.tests.stage1.tender_blanks import (
    tender_delivery_milestones as tender_delivery_milestones_forbidden,
)
from openprocurement.tender.limited.tests.base import (
    BaseTenderWebTest,
    test_lots,
    test_tender_negotiation_config,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_config,
    test_tender_negotiation_quick_data,
    test_tender_reporting_data,
)
from openprocurement.tender.limited.tests.tender_blanks import (
    changing_tender_after_award,
    create_tender,
    create_tender_accreditation,
    create_tender_generated,
    create_tender_invalid,
    create_tender_invalid_config,
    field_relatedLot,
    field_relatedLot_negotiation,
    initial_lot_date,
    listing,
    listing_changes,
    multiple_awards_tender,
    patch_tender,
    single_award_tender,
    tender_award_create,
    tender_cancellation,
    tender_cause,
    tender_cause_choices,
    tender_cause_desc,
    tender_cause_quick,
    tender_cause_reporting,
    tender_negotiation_status_change,
    tender_set_fund_organizations,
    tender_status_change,
    tender_with_main_procurement_category,
)
from openprocurement.tender.open.tests.tender_blanks import tender_finance_milestones
from openprocurement.tender.openua.tests.tender_blanks import empty_listing


class AccreditationTenderTest(BaseTenderWebTest):
    initial_data = test_tender_reporting_data

    test_create_tender_accreditation = snitch(create_tender_accreditation)


class TenderTest(BaseTenderWebTest):
    initial_data = test_tender_reporting_data
    test_tender_milestones_not_required = snitch(tender_milestones_not_required)
    test_tender_set_fund_organizations = snitch(tender_set_fund_organizations)
    test_tender_cause = snitch(tender_cause_reporting)


class TenderResourceTest(BaseTenderWebTest):
    initial_data = test_tender_reporting_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_tender_award_create = snitch(tender_award_create)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_create_tender_invalid_config = snitch(create_tender_invalid_config)
    test_field_relatedLot = snitch(field_relatedLot)
    test_create_tender_generated = snitch(create_tender_generated)
    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender = snitch(create_tender)
    test_create_tender_central = snitch(create_tender_central)
    test_create_tender_central_invalid = snitch(create_tender_central_invalid)
    test_get_tender = snitch(get_tender)
    test_patch_tender = snitch(patch_tender)
    patch_tender_draft = snitch(patch_tender_draft)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_tender_funders = snitch(tender_funders)
    test_tender_with_main_procurement_category = snitch(tender_with_main_procurement_category)
    test_tender_finance_milestones = snitch(tender_finance_milestones)
    test_create_tender_with_inn = snitch(create_tender_with_inn)
    test_create_tender_with_earlier_non_required_unit = snitch(create_tender_with_earlier_non_required_unit)
    test_create_tender_with_required_unit = snitch(create_tender_with_required_unit)
    test_patch_items_related_buyer_id = snitch(patch_items_related_buyer_id)
    test_create_tender_config_test = snitch(create_tender_config_test)
    test_tender_delivery_milestones = snitch(tender_delivery_milestones_forbidden)


class TenderNegotiationResourceTest(TenderResourceTest):
    initial_data = test_tender_negotiation_data
    initial_lots = test_lots_data = test_lots
    initial_config = test_tender_negotiation_config

    test_field_relatedLot = snitch(field_relatedLot_negotiation)
    test_changing_tender_after_award = snitch(changing_tender_after_award)
    test_initial_lot_date = snitch(initial_lot_date)
    test_patch_tender_lots_none = snitch(patch_tender_lots_none)
    test_tender_delivery_milestones = snitch(tender_delivery_milestones)


class TenderNegotiationQuickResourceTest(TenderNegotiationResourceTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config

    test_tender_delivery_milestones = snitch(tender_delivery_milestones)


class TenderProcessTest(BaseTenderWebTest):
    test_tender_status_change = snitch(tender_status_change)
    test_single_award_tender = snitch(single_award_tender)
    test_multiple_awards_tender = snitch(multiple_awards_tender)
    test_tender_cancellation = snitch(tender_cancellation)


class TenderNegotiationProcessTest(TenderProcessTest):
    initial_data = test_tender_negotiation_data
    initial_lots = test_lots
    initial_config = test_tender_negotiation_config

    test_tender_status_change = snitch(tender_negotiation_status_change)
    test_tender_cause = snitch(tender_cause)
    test_tender_cause_choices = snitch(tender_cause_choices)
    test_tender_cause_desc = snitch(tender_cause_desc)
    test_tender_milestones_required = snitch(tender_milestones_required)


class TenderNegotiationQuickProcessTest(TenderNegotiationProcessTest):
    initial_data = test_tender_negotiation_quick_data
    initial_config = test_tender_negotiation_quick_config

    test_tender_cause = snitch(tender_cause_quick)
    test_tender_cause_choices = snitch(tender_cause_choices)
    test_tender_cause_desc = snitch(tender_cause_desc)
    test_tender_milestones_required = snitch(tender_milestones_required)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderProcessTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
