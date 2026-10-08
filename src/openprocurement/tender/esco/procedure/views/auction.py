from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue
from openprocurement.tender.esco.procedure.serializers.auction import AuctionSerializer
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


@resource(
    name="esco:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="esco",
    description="Tender ESCO Auction data",
)
class ESCOTenderAuctionResource(TenderAuctionResource):
    state_class = ESCOTenderState
    serializer_class = AuctionSerializer

    @json_view(
        permission="auction",
    )
    def collection_post(self):
        # for esco we also calculate and update amountPerformance and amount
        self.state.validate_auction_post_request()
        tender_bids = {b["id"]: b for b in self.request.validated["tender"].get("bids", "")}
        for passed_bid in self.request.validated["data"]["bids"]:
            if "value" in passed_bid:
                value = tender_bids[passed_bid["id"]]["value"].copy()
                value.update(passed_bid["value"])
                passed_bid["value"] = ESCODynamicValue(value).serialize()
        return self.report_auction_results()

    @json_view(
        permission="auction",
    )
    def post(self):
        self.state.validate_auction_post_request()
        bid_values = {
            b["id"]: {lot["relatedLot"]: lot["value"] for lot in b.get("lotValues", "")}
            for b in self.request.validated["tender"].get("bids", "")
        }

        for passed_bid in self.request.validated["data"]["bids"]:
            if "lotValues" in passed_bid:
                for lv in passed_bid.get("lotValues", ""):
                    value = lv.get("value")
                    if value:
                        value = bid_values[passed_bid["id"]][lv["relatedLot"]].copy()
                        value.update(lv["value"])
                        lv["value"] = ESCODynamicValue(value).serialize()
        return self.report_lot_auction_results()
