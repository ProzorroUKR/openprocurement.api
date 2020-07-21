# -*- coding: utf-8 -*-
from openprocurement.api.validation import OPERATIONS
from openprocurement.api.utils import\
    get_now, json_view, context_unpack, raise_operation_error
from openprocurement.tender.core.utils import optendersresource, apply_patch
from openprocurement.tender.core.validation import (
    validate_patch_bid_data,
    validate_bid_operation_period,
    validate_bid_operation_not_in_tendering,
)

from openprocurement.tender.belowthreshold.views.bid import\
    TenderBidResource as BaseTenderBidResource
from openprocurement.tender.belowthreshold.validation import\
    validate_update_bid_status
from openprocurement.tender.pricequotation.constants import PMT


@optendersresource(
    name="{}:Tender Bids".format(PMT),
    collection_path="/tenders/{tender_id}/bids",
    path="/tenders/{tender_id}/bids/{bid_id}",
    procurementMethodType=PMT,
    description="Tender bids",
)
class TenderBidResource(BaseTenderBidResource):
    """ PriceQuotation tender bid resource """
    @json_view(
        content_type="application/json",
        permission="edit_bid",
        validators=(
            validate_patch_bid_data,
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period,
            validate_update_bid_status,
        ),
    )
    def patch(self):
        value = self.request.validated["data"].get("value") and self.request.validated["data"]["value"].get("amount")
        if value and value != self.request.context.get("value", {}).get("amount"):
            self.request.validated["data"]["date"] = get_now().isoformat()
        self.request.validated["tender"].modified = False
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info(
                "Updated tender bid {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_bid_patch"}),
            )
            return {"data": self.request.context.serialize("view")}

    @json_view(
        permission="edit_bid",
        validators=(
            validate_bid_operation_not_in_tendering,
            validate_bid_operation_period
        )
    )
    def delete(self):
        """
        Cancelling the proposal.
        Forbidden for price quotation tender.
        """
        request = self.request
        raise_operation_error(
            request,
            "Can't {} bid in Price Quotation tender".format(
                OPERATIONS.get(request.method),
            ),
        )
