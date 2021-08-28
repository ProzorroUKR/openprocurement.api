from openprocurement.tender.openuadefense.procedure.views.bid_document import UADefenseTenderBidDocumentResource
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense bidder documents",
)
class SimpleDefenseTenderBidDocumentResource(UADefenseTenderBidDocumentResource):
    pass
