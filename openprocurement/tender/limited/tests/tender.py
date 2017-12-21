# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    # TenderResourceTest
    listing_draft,
    create_tender_draft,
    get_tender,
    dateModified_tender,
    tender_not_found,
    tender_funders,
)

from openprocurement.tender.limited.tests.base import (
    BaseTenderWebTest,
    test_lots,
    test_tender_data,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)
from openprocurement.tender.limited.tests.tender_blanks import (
    # TenderNegotiationQuickProcessTest
    tender_cause_quick,
    # TenderNegotiationProcessTest
    tender_cause,
    # TenderProcessTest
    tender_status_change,
    single_award_tender,
    multiple_awards_tender,
    tender_cancellation,
    # TenderNegotiationResourceTest
    field_relatedLot_negotiation,
    changing_tender_after_award,
    initial_lot_date,
    # TenderResourceTest
    listing,
    tender_award_create,
    listing_changes,
    create_tender_invalid,
    field_relatedLot,
    create_tender_generated,
    create_tender,
    patch_tender,
    tender_Administrator_change,
    # TenderNegotiationQuickTest
    simple_add_tender_negotiation_quick,
    # TenderNegotiationTest
    simple_add_tender_negotiation,
    # TenderTest
    simple_add_tender,
    # AccreditationTenderTest
    create_tender_accreditation,
)

from openprocurement.tender.openua.tests.tender_blanks import (
    # TenderResourceTest
    empty_listing,
)


class AccreditationTenderTest(BaseTenderWebTest):
    initial_data = test_tender_data

    test_create_tender_accreditation = snitch(create_tender_accreditation)


class TenderTest(BaseTenderWebTest):
    initial_data = test_tender_data

    test_simple_add_tender = snitch(simple_add_tender)


class TenderNegotiationTest(BaseTenderWebTest):
    initial_data = test_tender_negotiation_data

    test_simple_add_tender = snitch(simple_add_tender_negotiation)


class TenderNegotiationQuickTest(TenderNegotiationTest):
    initial_data = test_tender_negotiation_quick_data

    test_simple_add_tender = snitch(simple_add_tender_negotiation_quick)


class TenderResourceTest(BaseTenderWebTest):
    initial_data = test_tender_data

    test_empty_listing = snitch(empty_listing)
    test_listing = snitch(listing)
    test_tender_award_create = snitch(tender_award_create)
    test_listing_changes = snitch(listing_changes)
    test_listing_draft = snitch(listing_draft)
    test_create_tender_invalid = snitch(create_tender_invalid)
    test_field_relatedLot = snitch(field_relatedLot)
    test_create_tender_generated = snitch(create_tender_generated)
    test_create_tender_draft = snitch(create_tender_draft)
    test_create_tender = snitch(create_tender)
    test_get_tender = snitch(get_tender)
    test_patch_tender = snitch(patch_tender)
    test_dateModified_tender = snitch(dateModified_tender)
    test_tender_not_found = snitch(tender_not_found)
    test_tender_Administrator_change = snitch(tender_Administrator_change)
    test_tender_funders = snitch(tender_funders)


class TenderNegotiationResourceTest(TenderResourceTest):
    initial_data = test_tender_negotiation_data
    test_lots_data = test_lots  # TODO: change attribute identifier

    test_field_relatedLot = snitch(field_relatedLot_negotiation)
    test_changing_tender_after_award = snitch(changing_tender_after_award)
    test_initial_lot_date = snitch(initial_lot_date)


class TenderNegotiationQuickResourceTest(TenderNegotiationResourceTest):
    initial_data = test_tender_negotiation_quick_data


class TenderProcessTest(BaseTenderWebTest):

    test_tender_status_change = snitch(tender_status_change)
    test_single_award_tender = snitch(single_award_tender)
    test_multiple_awards_tender = snitch(multiple_awards_tender)
    test_tender_cancellation = snitch(tender_cancellation)


class TenderNegotiationProcessTest(TenderProcessTest):
    initial_data = test_tender_negotiation_data

    test_tender_cause = snitch(tender_cause)


class TenderNegotiationQuickProcessTest(TenderNegotiationProcessTest):
    initial_data = test_tender_negotiation_quick_data

    test_tender_cause = snitch(tender_cause_quick)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderTest))
    suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
