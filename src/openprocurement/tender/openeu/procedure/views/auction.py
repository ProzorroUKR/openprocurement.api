from cornice.resource import resource

from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.openeu.procedure.models.auction import AuctionLotResults, AuctionResults
from openprocurement.tender.core.procedure.validation import (
    validate_auction_tender_status,
    validate_auction_tender_non_lot,
    validate_input_data,
    validate_active_lot,
)


@resource(
    name="aboveThresholdEU:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU auction data",
)
class EUTenderAuctionResource(TenderAuctionResource):
    state_class = OpenEUTenderState

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        )
    )
    def collection_post(self):
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
        return super().post()
