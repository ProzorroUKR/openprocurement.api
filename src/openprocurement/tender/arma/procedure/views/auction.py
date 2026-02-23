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
    patch_value_field_names = {"value", "initialValue", "weightedValue"}

    def patch_from_auction_data(self, data):
        """
        Method patches auction results to fit ARMA structure
        """

        def _patch_value(value):
            value.pop("currency", None)
            value.pop("valueAddedTaxIncluded", None)
            amount = value.pop("amount", None)
            if amount is not None:
                value["amountPercentage"] = amount

        for bid in data["bids"]:
            for value_field in self.patch_value_field_names:
                if val := bid.get(value_field):
                    _patch_value(val)

            if "lotValues" in bid:
                for l_value in bid["lotValues"]:
                    for value_field in self.patch_value_field_names:
                        if val := l_value.get(value_field):
                            _patch_value(val)

        return data

    def patch_to_auction_data(self, data):
        """
        Method patches ARMA structure to fit auction structure
        """

        def _patch_value(value):
            value["currency"] = "%"
            amount_percentage = value.pop("amountPercentage", None)
            if amount_percentage is not None:
                value["amount"] = amount_percentage

        for bid in data["data"]["bids"]:
            for value_field in self.patch_value_field_names:
                if val := bid.get(value_field):
                    _patch_value(val)

            if "lotValues" in bid:
                for l_value in bid["lotValues"]:
                    for value_field in self.patch_value_field_names:
                        if val := l_value.get(value_field):
                            _patch_value(val)

        return data

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        ),
    )
    def collection_post(self):
        self.request.validated["data"] = self.patch_from_auction_data(self.request.validated["data"])
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
        self.request.validated["data"] = self.patch_from_auction_data(self.request.validated["data"])
        return super().post()

    @json_view(
        permission="auction",
        validators=(validate_auction_tender_status,),
    )
    def collection_get(self):
        return self.patch_to_auction_data(super().collection_get())
