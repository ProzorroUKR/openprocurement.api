from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.api.procedure.validation import validate_request_by_state
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.auction_period_start_date import (
    AuctionPeriodStartDateState,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.base import TenderBaseResource


@resource(
    name="Tender Auction Period Start Date",
    collection_path="/tenders/{tender_id}/auctionPeriod",
    path="/tenders/{tender_id}/lots/{lot_id}/auctionPeriod",
    description="Tender auctionPeriod start date",
)
class TenderAuctionPeriodResource(TenderBaseResource):
    state_class = AuctionPeriodStartDateState

    def __acl__(self):
        return [(Allow, "g:Administrator", "edit_action_period")]

    @json_view(
        content_type="application/json",
        permission="edit_action_period",
        validators=(validate_request_by_state,),
    )
    def collection_put(self):
        tender = self.request.validated["tender"]
        data = self.request.validated["data"]
        self.state.validate_auction_period_start_date(tender, data)
        if "auctionPeriod" not in tender:
            tender["auctionPeriod"] = {}
        tender["auctionPeriod"]["startDate"] = data["startDate"]

        save_tender(self.request)
        return tender["auctionPeriod"]

    @json_view(
        content_type="application/json",
        permission="edit_action_period",
        validators=(validate_request_by_state,),
    )
    def put(self):
        lot_id = self.request.matchdict["lot_id"]
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        self.state.validate_auction_period_start_date(tender, data)
        for lot in tender["lots"]:
            if lot["id"] == lot_id:
                if "auctionPeriod" not in lot:
                    lot["auctionPeriod"] = {}
                lot["auctionPeriod"]["startDate"] = data["startDate"]
                save_tender(self.request)
                return lot["auctionPeriod"]
