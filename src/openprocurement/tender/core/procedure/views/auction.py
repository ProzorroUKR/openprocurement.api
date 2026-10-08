from openprocurement.api.procedure.utils import apply_data_patch
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.constants import AUCTION_SET_URLS_LOG_FIELDS
from openprocurement.tender.core.procedure.serializers.auction import AuctionSerializer
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    filter_nested_values,
    save_tender,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


class TenderAuctionResource(TenderBaseResource):
    serializer_class = AuctionSerializer
    state_class = TenderState

    @json_view(
        permission="auction",
    )
    def collection_get(self):
        self.state.validate_auction_get_request()
        tender = self.request.validated["tender"]
        data = self.serializer_class(tender).data

        LOG_CONTEXT = {
            "raw_data": filter_nested_values(tender, *AUCTION_SET_URLS_LOG_FIELDS),
            "serialized_data": filter_nested_values(data, *AUCTION_SET_URLS_LOG_FIELDS),
        }
        self.LOGGER.info(
            "Get tender by auction",
            extra=context_unpack(
                self.request,
                {"MESSAGE_ID": "tender_by_auction_get"},
                {"CONTEXT": LOG_CONTEXT},
            ),
        )

        return {
            "data": data,
            "config": tender["config"],
        }

    @json_view(
        permission="auction",
    )
    def collection_patch(self):
        """Set urls to access auctions."""
        self.state.validate_auction_patch_request()
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]

        # apply data patch and update tender state
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated
            self.state.on_patch(tender_src, tender)

        # save tender
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
    )
    def patch(self):
        """Set urls for access to auction for lot."""
        self.state.validate_auction_patch_request()
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        tender_src = self.request.validated["tender_src"]

        # apply data patch and update tender state
        updated = apply_data_patch(tender, data)
        if updated:
            tender = self.request.validated["tender"] = updated
            self.state.on_auction_patch(tender_src, tender)
            self.state.on_patch(tender_src, tender)

        # save tender
        if save_tender(self.request):
            LOG_CONTEXT = {
                "before": filter_nested_values(tender_src, *AUCTION_SET_URLS_LOG_FIELDS),
                "after": filter_nested_values(tender, *AUCTION_SET_URLS_LOG_FIELDS),
            }
            self.LOGGER.info(
                "Updated auction urls",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_lot_auction_patch"},
                    {"CONTEXT": LOG_CONTEXT},
                ),
            )

            return {
                "data": self.serializer_class(tender).data,
                "config": tender["config"],
            }

    @json_view(
        permission="auction",
    )
    def collection_post(self):
        """Report auction results."""
        self.state.validate_auction_post_request()
        return self.report_auction_results()

    def report_auction_results(self):
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
    )
    def post(self):
        """Report auction results for lot."""
        self.state.validate_auction_post_request()
        return self.report_lot_auction_results()

    def report_lot_auction_results(self):
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
