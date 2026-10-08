from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)
from openprocurement.tender.open.constants import OPEN_PROCUREMENT_METHOD_TYPES, OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    description="Tender bidder documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseTenderBidDocumentResource(BaseTenderBidDocumentResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    description="Tender bidder eligibility documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseTenderBidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    description="Tender bidder financial documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseTenderBidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    description="Tender bidder qualification documents",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseTenderBidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    pass
