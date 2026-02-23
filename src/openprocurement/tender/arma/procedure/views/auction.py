from cornice.resource import resource

from openprocurement.api.procedure.validation import validate_input_data
from openprocurement.api.utils import json_view
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.models.auction import (
    AuctionLotResults,
    AuctionResults,
)
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.validation import (
    validate_active_lot,
    validate_auction_tender_status,
)
from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender auction data",
)
class AuctionResource(TenderAuctionResource):
    state_class = TenderState

    def morph_auction_results(self):
        """
        Method morphs auction results to fit ARMA structure
        """

        def _morph_value(value):
            value.pop("currency", None)
            value.pop("valueAddedTaxIncluded", None)
            if amount_percentage := value.pop("amount", None):
                value["amountPercentage"] = amount_percentage

        data = self.request.validated["data"]
        for bid in data["bids"]:
            if "value" in bid:
                _morph_value(bid["value"])
            if "lotValues" in bid:
                for l_value in bid["lotValues"]:
                    _morph_value(l_value["value"])
            if "weightedValue" in bid:
                _morph_value(bid["weightedValue"])

        self.request.validated["data"] = data

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        ),
    )
    def collection_post(self):
        self.morph_auction_results()
        return super().collection_post()

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_active_lot,
            validate_input_data(AuctionLotResults),
        ),
    )
    def post(self):
        self.morph_auction_results()
        return super().post()
