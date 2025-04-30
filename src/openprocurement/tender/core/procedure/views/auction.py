from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.models.auction import (
    AuctionLotResults,
    AuctionResults,
    AuctionUrls,
    LotAuctionUrls,
)
from openprocurement.tender.core.procedure.serializers.auction import AuctionSerializer
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    validate_active_lot,
    validate_auction_tender_non_lot,
    validate_auction_tender_status,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


class TenderAuctionResource(TenderBaseResource):
    serializer_class = AuctionSerializer
    state_class = TenderState

    @json_view(
        permission="auction",
        validators=(validate_auction_tender_status,),
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        return {
            "data": self.serializer_class(tender).data,
            "config": tender["config"],
        }

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_auction_tender_non_lot,
            validate_input_data(AuctionUrls),
        ),
    )
    def collection_patch(self):
        """Set urls to access auctions."""
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated
            self.state.on_patch(tender_src, tender)

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated auction urls",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_auction_patch"}),
            )
            return {
                "data": self.serializer_class(tender).data,
                "config": tender["config"],
            }

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_active_lot,
            validate_input_data(LotAuctionUrls),
        ),
    )
    def patch(self):
        """Set urls for access to auction for lot."""
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated
            self.state.on_patch(tender_src, tender)
        if save_tender(self.request):
            self.LOGGER.info(
                "Updated auction urls",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_patch"}),
            )
            return {
                "data": self.serializer_class(tender).data,
                "config": tender["config"],
            }

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        ),
    )
    def collection_post(self):
        """Report auction results."""
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated
        self.state.on_auction_results(tender)
        self.state.on_patch(tender_src, tender)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_auction_post"}),
            )
            return {
                "data": self.serializer_class(tender).data,
                "config": tender["config"],
            }

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_active_lot,
            validate_input_data(AuctionLotResults),
        ),
    )
    def post(self):
        """Report auction results for lot."""
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]
        lot_id = self.request.matchdict.get("auction_lot_id")
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated
        self.state.on_auction_results(tender, lot_id)
        self.state.on_patch(tender_src, tender)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results",
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_post"}),
            )
            return {
                "data": self.serializer_class(tender).data,
                "config": tender["config"],
            }
