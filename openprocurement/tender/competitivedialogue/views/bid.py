# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.validation import validate_patch_bid_data
from openprocurement.api.utils import (
    apply_patch,
    opresource,
    save_tender,
    json_view,
    context_unpack,
)
from openprocurement.tender.openua.views.bid import TenderUABidResource as BaseResourceUA
from openprocurement.tender.openeu.views.bid import TenderBidResource as BaseResourceEU


@opresource(name='Competitive Dialogue EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue EU bids")
class CompetitiveDialogueEUBidResource(BaseResourceEU):
    """ Tender EU bids """
    pass


@opresource(name='Competitive Dialogue UA Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdUA',
            description="Competitive Dialogue UA bids")
class CompetitiveDialogueUABidResource(BaseResourceUA):
    """ Tender EU bids """
    pass

