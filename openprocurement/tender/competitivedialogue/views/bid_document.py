# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    opresource
)
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource
from openprocurement.tender.openeu.utils import (
    bid_financial_documents_resource, bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)


@opresource(
    name='Competitive Dialogue EU Bid Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU bidder documents")
class CompetitiveDialogueEUBidDocumentResource(TenderEUBidDocumentResource):
    pass


@opresource(
    name='Competitive Dialogue UA Bid Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdUA',
    description="Competitive Dialogue UA bidder documents")
class CompetitiveDialogueUaBidDocumentResource(TenderUaBidDocumentResource):
    pass


@bid_financial_documents_resource(
    name='Competitive Dialogue EU Bid Financial Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU bidder financial documents")
class CompetitiveDialogueEUBidFinancialDocumentResource(TenderEUBidDocumentResource):
    """ Tender EU Bid Financial Documents """

    container = "financialDocuments"
    view_forbidden_states = ['active.tendering', 'active.pre-qualification',
                             'active.pre-qualification.stand-still']


@bid_eligibility_documents_resource(
    name='Competitive Dialogue EU Bid Eligibility Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU bidder eligibility documents")
class CompetitiveDialogueEUBidEligibilityDocumentResource(CompetitiveDialogueEUBidFinancialDocumentResource):
    """ Tender EU Bid Eligibility Documents """
    container = "eligibilityDocuments"


@bid_qualification_documents_resource(
    name='Competitive Dialogue EU Bid Qualification Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}',
    procurementMethodType='competitiveDialogue.aboveThresholdEU',
    description="Competitive Dialogue EU bidder qualification documents")
class TenderEUBidQualificationDocumentResource(CompetitiveDialogueEUBidFinancialDocumentResource):
    """ Tender EU Bid Qualification Documents """
    container = "qualificationDocuments"
