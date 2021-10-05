from openprocurement.tender.core.procedure.views.auction import TenderAuctionResource
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from openprocurement.api.utils import raise_operation_error
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Auction",
    collection_path="/tenders/{tender_id}/auction",
    path="/tenders/{tender_id}/auction/{auction_lot_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender auction data",
)
class TenderAuctionResource(TenderAuctionResource):
    state_class = CFASelectionTenderState

    def collection_patch(self):
        raise_operation_error(self.request, "Not implemented", status=405)

    def collection_post(self):
        raise_operation_error(self.request, "Not implemented", status=405)
