from openprocurement.tender.openua.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderTenderState
from openprocurement.tender.esco.procedure.serializers.auction import AuctionSerializer
from openprocurement.tender.esco.procedure.models.value import ESCOValue
from openprocurement.tender.esco.procedure.models.auction import AuctionResults, AuctionLotResults
from cornice.resource import resource
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    validate_auction_tender_status,
    validate_input_data,
    validate_active_lot,
)


@resource(
    name="esco:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="esco",
    description="Tender ESCO Auction data",
)
class ESCOTenderAuctionResource(TenderAuctionResource):
    state_class = ESCOTenderTenderState
    serializer_class = AuctionSerializer

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        )
    )
    def collection_post(self):
        # for esco we also calculate and update amountPerformance and amount
        tender_bids = {b["id"]: b for b in self.request.validated["tender"].get("bids", "")}
        for passed_bid in self.request.validated["data"]["bids"]:
            if "value" in passed_bid:
                value = tender_bids[passed_bid["id"]]["value"].copy()
                value.update(passed_bid["value"])
                passed_bid["value"] = ESCOValue(value).serialize()
        return super().collection_post()

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_active_lot,
            validate_input_data(AuctionLotResults),
        )
    )
    def post(self):
        bid_values = {b["id"]: {l["relatedLot"]: l["value"] for l in b.get("lotValues", "")}
                      for b in self.request.validated["tender"].get("bids", "")}

        for passed_bid in self.request.validated["data"]["bids"]:
            if "lotValues" in passed_bid:
                for lv in passed_bid.get("lotValues", ""):
                    value = lv.get("value")
                    if value:
                        value = bid_values[passed_bid["id"]][lv["relatedLot"]].copy()
                        value.update(lv["value"])
                        lv["value"] = ESCOValue(value).serialize()
        return super().post()
