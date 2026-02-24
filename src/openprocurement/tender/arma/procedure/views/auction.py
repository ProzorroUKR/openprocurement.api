from typing import Callable

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
    patch_value_field_names = {"value", "initialValue", "weightedValue", "minimalStep"}

    @staticmethod
    def convert_value_from_auction(value: dict):
        """
        Method converts data to fit tender value format
        """
        value.pop("currency", None)
        value.pop("valueAddedTaxIncluded", None)
        amount = value.pop("amount", None)
        if amount is not None:
            value["amountPercentage"] = amount

    @staticmethod
    def convert_value_to_auction(value: dict):
        """
        Method converts data to fit auction value format
        """
        value["currency"] = "%"
        amount_percentage = value.pop("amountPercentage", None)
        if amount_percentage is not None:
            value["amount"] = amount_percentage

    def convert_value_data(self, data: dict, patch_value_callable: Callable) -> dict:
        """
        Method converts data to fit expected structure
        """
        for bid in data.get("bids", []):
            for value_field in self.patch_value_field_names:
                if val := bid.get(value_field):
                    patch_value_callable(val)

            for l_value in bid.get("lotValues", []):
                for value_field in self.patch_value_field_names:
                    if val := l_value.get(value_field):
                        patch_value_callable(val)

        for lot in data.get("lots", []):
            for value_field in self.patch_value_field_names:
                if val := lot.get(value_field):
                    patch_value_callable(val)

        return data

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        ),
    )
    def collection_post(self):
        self.request.validated["data"] = self.convert_value_data(
            self.request.validated["data"], self.convert_value_from_auction
        )
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
        self.request.validated["data"] = self.convert_value_data(
            self.request.validated["data"], self.convert_value_from_auction
        )
        return super().post()

    @json_view(
        permission="auction",
        validators=(validate_auction_tender_status,),
    )
    def collection_get(self):
        res = super().collection_get()
        res["data"] = self.convert_value_data(res["data"], self.convert_value_to_auction)
        return res
