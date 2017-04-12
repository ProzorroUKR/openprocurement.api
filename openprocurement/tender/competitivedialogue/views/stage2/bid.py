# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import (
    optendersresource
)
from openprocurement.tender.core.validation import (
    validate_bid_data,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering
)
from openprocurement.tender.openeu.views.bid import (
    TenderBidResource as BaseResourceEU
)
from openprocurement.tender.openua.views.bid import (
    TenderUABidResource as BaseResourceUA
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
)
from openprocurement.tender.competitivedialogue.utils import stage2_bid_post
from openprocurement.tender.competitivedialogue.validation import validate_firm_to_create_bid

@optendersresource(name='{}:Tender Bids'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/bids',
                   path='/tenders/{tender_id}/bids/{bid_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue  Stage2EU bids")
class CompetitiveDialogueStage2EUBidResource(BaseResourceEU):
    """ Tender Stage2 EU  bids """
    allowed_bid_status_on_create = ['draft', 'pending']

    @json_view(content_type="application/json", permission='create_bid', validators=(validate_bid_data, validate_bid_operation_not_in_tendering,
               validate_bid_operation_period, validate_firm_to_create_bid))
    def collection_post(self):
        return stage2_bid_post(self)


@optendersresource(name='{}:Tender Bids'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/bids',
                   path='/tenders/{tender_id}/bids/{bid_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage2 UA bids")
class CompetitiveDialogueStage2UABidResource(BaseResourceUA):
    """ Tender Stage2 UA Stage2 bids """
    allowed_bid_status_on_create = ['draft', 'active']

    @json_view(content_type="application/json", permission='create_bid', validators=(validate_bid_data, validate_bid_operation_not_in_tendering,
               validate_bid_operation_period, validate_firm_to_create_bid))
    def collection_post(self):
        return stage2_bid_post(self)
