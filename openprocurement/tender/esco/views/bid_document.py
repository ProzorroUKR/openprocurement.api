# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource,
    bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)


@optendersresource(name='esco.EU:Tender Bid Documents',
                   collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
                   path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU bidder documents")
class TenderESCOEUBidDocumentResource(TenderEUBidDocumentResource):
    """ Tender ESCO EU Bid Document Resource """

@bid_financial_documents_resource(
    name='escoEU:Tender Bid Financial Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType='esco.EU',
    description="Tender ESCO EU bidder financial documents")
class TenderESCOEUBidFinancialDocumentResource(TenderESCOEUBidDocumentResource):
    """ Tender ESCO EU Bid Financial Documents """
    container = "financialDocuments"
    view_forbidden_states = ['active.tendering', 'active.pre-qualification',
                             'active.pre-qualification.stand-still', 'active.auction']
    view_forbidden_bid_states = ['invalid', 'deleted', 'invalid.pre-qualification', 'unsuccessful']

@bid_eligibility_documents_resource(
    name='escoEU:Tender Bid Eligibility Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}',
    procurementMethodType='esco.EU',
    description="Tender ESCO EU bidder eligibility documents")
class TenderESCOEUBidEligibilityDocumentResource(TenderESCOEUBidFinancialDocumentResource):
    """ Tender ESCO EU Bid Eligibility Documents """
    container = "eligibilityDocuments"
    view_forbidden_states = ['active.tendering']
    view_forbidden_bid_states = ['invalid', 'deleted']


@bid_qualification_documents_resource(
    name='escoEU:Tender Bid Qualification Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}',
    procurementMethodType='esco.EU',
    description="Tender ESCO EU bidder qualification documents")
class TenderESCOEUBidQualificationDocumentResource(TenderESCOEUBidFinancialDocumentResource):
    """ Tender ESCO EU Bid Qualification Documents """
    container = "qualificationDocuments"
