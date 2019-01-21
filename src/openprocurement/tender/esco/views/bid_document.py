# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource,
    bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)


@optendersresource(name='esco:Tender Bid Documents',
                   collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
                   path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
                   procurementMethodType='esco',
                   description="Tender ESCO bidder documents")
class TenderESCOBidDocumentResource(TenderEUBidDocumentResource):
    """ Tender ESCO Bid Document Resource """


@bid_financial_documents_resource(
    name='esco:Tender Bid Financial Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType='esco',
    description="Tender ESCO bidder financial documents")
class TenderESCOBidFinancialDocumentResource(TenderESCOBidDocumentResource):
    """ Tender ESCO Bid Financial Documents """
    container = "financialDocuments"
    view_forbidden_states = ['active.tendering', 'active.pre-qualification',
                             'active.pre-qualification.stand-still', 'active.auction']
    view_forbidden_bid_states = ['invalid', 'deleted', 'invalid.pre-qualification', 'unsuccessful']


@bid_eligibility_documents_resource(
    name='esco:Tender Bid Eligibility Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}',
    procurementMethodType='esco',
    description="Tender ESCO bidder eligibility documents")
class TenderESCOBidEligibilityDocumentResource(TenderESCOBidFinancialDocumentResource):
    """ Tender ESCO Bid Eligibility Documents """
    container = "eligibilityDocuments"
    view_forbidden_states = ['active.tendering']
    view_forbidden_bid_states = ['invalid', 'deleted']


@bid_qualification_documents_resource(
    name='esco:Tender Bid Qualification Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}',
    procurementMethodType='esco',
    description="Tender ESCO bidder qualification documents")
class TenderESCOBidQualificationDocumentResource(TenderESCOBidFinancialDocumentResource):
    """ Tender ESCO Bid Qualification Documents """
    container = "qualificationDocuments"
