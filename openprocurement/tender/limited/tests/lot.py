# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import snitch

from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_lots,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data
)
from openprocurement.tender.limited.tests.lot_blanks import (
    # TenderLotNegotiationResourceTest
    create_tender_lot_invalid,
    create_tender_lot,
    create_complete_tender_lot,
    create_cancelled_tender_lot,
    create_unsuccessful_tender_lot,
    patch_tender_lot,
    patch_tender_currency,
    patch_tender_vat,
    delete_unsuccessful_tender_lot,
    delete_tender_lot,
    delete_complete_tender_lot,
    cancel_lot_after_sing_contract,
    cancel_lot_with_complaint,
    last_lot_complete,
    all_cancelled_lots,
    cancel_lots_check_awards,
    delete_lot_after_first_award,
    patch_lot_with_cancellation,
)


class TenderLotNegotiationResourceTest(BaseTenderContentWebTest):
    initial_status = 'active'
    initial_data = test_tender_negotiation_data
    initial_bids = None  # test_bids
    test_lots_data = test_lots  # TODO: change attribute identifier

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_create_complete_tender_lot = snitch(create_complete_tender_lot)
    test_create_cancelled_tender_lot = snitch(create_cancelled_tender_lot)
    test_create_unsuccessful_tender_lot = snitch(create_unsuccessful_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_delete_unsuccessful_tender_lot = snitch(delete_unsuccessful_tender_lot)
    test_delete_tender_lot = snitch(delete_tender_lot)
    test_delete_complete_tender_lot = snitch(delete_complete_tender_lot)
    test_cancel_lot_after_sing_contract = snitch(cancel_lot_after_sing_contract)
    test_cancel_lot_with_complaint = snitch(cancel_lot_with_complaint)
    test_last_lot_complete = snitch(last_lot_complete)
    test_all_cancelled_lots = snitch(all_cancelled_lots)
    test_cancel_lots_check_awards = snitch(cancel_lots_check_awards)
    test_delete_lot_after_first_award = snitch(delete_lot_after_first_award)
    test_patch_lot_with_cancellation = snitch(patch_lot_with_cancellation)


class TenderLotNegotiationQuickResourceTest(TenderLotNegotiationResourceTest):

    initial_data = test_tender_negotiation_quick_data
