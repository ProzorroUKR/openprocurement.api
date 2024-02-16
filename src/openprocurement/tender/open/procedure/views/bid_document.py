from cornice.resource import resource

from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender bidder documents",
)
class TenderBidDocumentResource(BaseTenderBidDocumentResource):
    pass


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender bidder eligibility documents",
)
class TenderBidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    pass


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender bidder financial documents",
)
class TenderBidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    pass


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender bidder qualification documents",
)
class TenderBidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    pass
