from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState
from cornice.resource import resource
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.validation import (
    validate_auction_tender_status,
    validate_input_data,
    validate_active_lot,
)
from openprocurement.tender.core.procedure.utils import save_tender, apply_data_patch
from openprocurement.tender.core.procedure.models.auction import AuctionLotResults


@resource(
    name="aboveThresholdUA.defense:Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense auction data",
)
class TenderAuctionResource(TenderAuctionResource):
    state_class = OpenUADefenseTenderState

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_active_lot,
            validate_input_data(AuctionLotResults),
        )
    )
    def post(self):
        """Report auction results for lot.
        """
        lot_id = self.request.matchdict.get("auction_lot_id")
        tender = self.request.validated["tender"]
        data = self.request.validated["data"]
        updated = apply_data_patch(self.request.validated["tender"], data)
        if updated:
            self.request.validated["tender"] = tender = updated

        for lot in tender["lots"]:
            if lot["id"] == lot_id:
                lot["auctionPeriod"].update(
                    self.get_auction_period()
                )
                break

        if all(
            i.get("auctionPeriod") and i["auctionPeriod"].get("endDate")
            for i in tender["lots"]
            if i["status"] == "active" and self.state.count_lot_bids_number(tender, i["id"]) > 1
        ):
            self.state.add_next_award(self.request)

        self.state.on_patch(self.request.validated["tender_src"], self.request.validated["tender"])
        if save_tender(self.request):
            self.LOGGER.info(
                "Report auction results", extra=context_unpack(self.request, {"MESSAGE_ID": "tender_lot_auction_post"})
            )
            return {"data": self.serializer_class(tender).data}
