# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.bid import TenderBidResource as BaseResourceEU
from openprocurement.tender.openua.views.bid import TenderBidResource as BaseResourceUA
from openprocurement.tender.competitivedialogue.models import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
from openprocurement.tender.competitivedialogue.utils import stage2_bid_post
from openprocurement.api.utils import (
    opresource,
    json_view,
)
from openprocurement.api.validation import (
    validate_bid_data
)


@opresource(name='Competitive Dialogue Stage2 EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue  Stage2EU bids")
class CompetitiveDialogueStage2EUBidResource(BaseResourceEU):
    """ Tender Stage2 EU  bids """

    @json_view(content_type="application/json", permission='create_bid', validators=(validate_bid_data,))
    def collection_post(self):
        return stage2_bid_post(self)


@opresource(name='Competitive Dialogue Stage2 UA Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage2 UA bids")
class CompetitiveDialogueStage2UABidResource(BaseResourceUA):
    """ Tender Stage2 UA Stage2 bids """

    @json_view(content_type="application/json", permission='create_bid', validators=(validate_bid_data,))
    def collection_post(self):
        return stage2_bid_post(self)
