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
from openprocurement.tender.openua.views.bid import TenderUABidResource as BaseResource
from openprocurement.tender.competitivedialogue.utils import (bid_collection_get_eu, bid_get_eu, bid_patch_eu,
                                                              bid_delete_eu)


@opresource(name='Competitive Dialogue EU Bids',
            collection_path='/tenders/{tender_id}/bids',
            path='/tenders/{tender_id}/bids/{bid_id}',
            procurementMethodType='competitiveDialogue.aboveThresholdEU',
            description="Competitive Dialogue EU bids")
class CompetitiveDialogueEUBidResource(BaseResource):
    """ Tender EU bids """
    @json_view(permission='view_tender')
    def collection_get(self):
        return bid_collection_get_eu(self)

    @json_view(permission='view_tender')
    def get(self):
        return bid_get_eu(self)

    @json_view(content_type="application/json", permission='edit_bid', validators=(validate_patch_bid_data,))
    def patch(self):
        return bid_patch_eu(self)

    @json_view(permission='edit_bid')
    def delete(self):
        return bid_delete_eu(self)
