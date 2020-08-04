# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.bid import TenderUABidResource as TenderBidResource
from openprocurement.tender.core.validation import (
    validate_patch_bid_data,
    validate_update_deleted_bid,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.openua.validation import validate_update_bid_to_draft, validate_update_bid_to_active_status


@optendersresource(
    name="aboveThresholdUA.defense:Tender Bids",
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense bids",
)
class TenderUABidResource(TenderBidResource):
    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_deleted_bid,
            validate_update_bid_to_draft,
            validate_update_bid_to_active_status,
        ),
    )
    def patch(self):
        return super(TenderUABidResource, self).patch()
