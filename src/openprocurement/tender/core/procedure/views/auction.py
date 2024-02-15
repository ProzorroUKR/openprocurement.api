from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.validation import (
    validate_auction_tender_status,
    validate_auction_tender_non_lot,
    validate_active_lot,
)
from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.models.auction import (
    AuctionUrls,
    LotAuctionUrls,
    AuctionResults,
    AuctionLotResults,
)
from openprocurement.tender.core.procedure.serializers.auction import AuctionSerializer
from openprocurement.tender.core.procedure.utils import submission_method_details_includes
from openprocurement.tender.core.utils import QUICK_NO_AUCTION, QUICK_FAST_FORWARD, QUICK_FAST_AUCTION


class TenderAuctionResource(TenderBaseResource):
    serializer_class = AuctionSerializer
    state_class = TenderState

    @json_view(
        permission="auction",
        validators=(validate_auction_tender_status,),
    )
    def collection_get(self):
        tender = get_tender()
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
                "Updated auction urls", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_auction_patch"})
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
                "Updated auction urls", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_patch"})
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

        self.state.add_next_award()
        self.update_auction_period(tender)

        self.state.on_patch(tender_src, tender)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_auction_post"})
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

        for lot in tender["lots"]:
            if lot["id"] == lot_id:
                self.update_auction_period(lot)
                break
        if all(
            i.get("auctionPeriod") and i["auctionPeriod"].get("endDate")
            # I believe, bids number check only required for belowThreshold procedure
            # openua, for example, changes its lot.status to "unsuccessful"
            for i in tender["lots"]
            if i["status"] == "active" and self.state.count_lot_bids_number(tender, i["id"]) > 1
        ):
            self.state.add_next_award()

        self.state.on_patch(tender_src, tender)
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_post"})
            )
            return {
                "data": self.serializer_class(tender).data,
                "config": tender["config"],
            }

    def update_auction_period(self, obj):
        tender = self.request.validated["tender"]
        now = get_now().isoformat()
        quick_modes = (QUICK_NO_AUCTION, QUICK_FAST_FORWARD, QUICK_FAST_AUCTION)
        if not submission_method_details_includes(quick_modes, tender):
            obj["auctionPeriod"].update({"endDate": now})
        else:
            obj["auctionPeriod"].update({"startDate": now, "endDate": now})
