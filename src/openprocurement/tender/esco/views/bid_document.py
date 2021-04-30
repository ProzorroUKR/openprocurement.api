# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid_document import (
    TenderEUBidDocumentResource,
    TenderEUBidFinancialDocumentResource,
)
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource,
    bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)


# @optendersresource(
#     name="esco:Tender Bid Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO bidder documents",
# )
class TenderESCOBidDocumentResource(TenderEUBidDocumentResource):
    """ Tender ESCO Bid Document Resource """


# @bid_eligibility_documents_resource(
#     name="esco:Tender Bid Eligibility Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO bidder eligibility documents",
# )
class TenderESCOBidEligibilityDocumentResource(TenderEUBidDocumentResource):
    """ Tender ESCO Bid Eligibility Documents """

    container = "eligibilityDocuments"


# @bid_financial_documents_resource(
#     name="esco:Tender Bid Financial Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO bidder financial documents",
# )
class TenderESCOBidFinancialDocumentResource(TenderEUBidFinancialDocumentResource):
    """ Tender ESCO Bid Financial Documents """


# @bid_qualification_documents_resource(
#     name="esco:Tender Bid Qualification Documents",
#     collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
#     path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
#     procurementMethodType="esco",
#     description="Tender ESCO bidder qualification documents",
# )
class TenderESCOBidQualificationDocumentResource(TenderEUBidFinancialDocumentResource):
    """ Tender ESCO Bid Qualification Documents """

    container = "qualificationDocuments"
