from openprocurement.tender.openeu.procedure.views.bid_document import (
    OpenEUTenderBidDocumentResource,
    TenderEUBidFinancialDocumentResource,
)
from cornice.resource import resource


@resource(
    name="esco:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO bidder documents",
)
class ESCOTenderBidDocumentResource(OpenEUTenderBidDocumentResource):
    pass


@resource(
    name="esco:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO bidder eligibility documents",
)
class TenderESCOBidEligibilityDocumentResource(OpenEUTenderBidDocumentResource):
    container = "eligibilityDocuments"


@resource(
    name="esco:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO bidder financial documents",
)
class TenderESCOBidFinancialDocumentResource(TenderEUBidFinancialDocumentResource):
    container = "financialDocuments"


@resource(
    name="esco:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO bidder qualification documents",
)
class TenderESCOBidQualificationDocumentResource(TenderEUBidFinancialDocumentResource):
    container = "qualificationDocuments"

