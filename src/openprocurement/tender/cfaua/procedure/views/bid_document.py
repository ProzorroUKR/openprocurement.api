from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.bid_document import (
    CFAUABidDocumentState,
    CFAUABidFinancialDocumentState,
)
from openprocurement.tender.core.procedure.views.bid_document import (
    BaseTenderBidDocumentResource,
    BaseTenderBidEligibilityDocumentResource,
    BaseTenderBidFinancialDocumentResource,
    BaseTenderBidQualificationDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender bidder documents",
)
class TenderBidDocumentResource(BaseTenderBidDocumentResource):
    state_class = CFAUABidDocumentState


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender bidder eligibility documents",
)
class TenderBidEligibilityDocumentResource(BaseTenderBidEligibilityDocumentResource):
    state_class = CFAUABidDocumentState


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender bidder financial documents",
)
class TenderBidFinancialDocumentResource(BaseTenderBidFinancialDocumentResource):
    state_class = CFAUABidFinancialDocumentState


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender bidder qualification documents",
)
class TenderBidQualificationDocumentResource(BaseTenderBidQualificationDocumentResource):
    state_class = CFAUABidFinancialDocumentState
