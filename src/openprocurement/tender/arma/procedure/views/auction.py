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
    name="complexAsset.arma:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender auction data",
)
class AuctionResource(TenderAuctionResource):
    state_class = TenderState

    @json_view(
        permission="auction",
        validators=(
            validate_auction_tender_status,
            validate_input_data(AuctionResults),
        ),
    )
    def collection_post(self):
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
        return super().post()
