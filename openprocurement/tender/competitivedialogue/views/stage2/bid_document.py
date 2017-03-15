# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid_document import (
    bid_financial_documents_resource,
    bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
    TenderEUBidDocumentResource,
    TenderEUBidFinancialDocumentResource,
    TenderEUBidEligibilityDocumentResource,
    TenderEUBidQualificationDocumentResource
)
from openprocurement.tender.openua.views.bid_document import (
    TenderUaBidDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
)

@optendersresource(
    name='{}:Tender Bid Documents'.format(STAGE_2_EU_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder documents")
class CompetitiveDialogueStage2EUBidDocumentResource(TenderEUBidDocumentResource):
    pass


@optendersresource(
    name='{}:Tender Bid Documents'.format(STAGE_2_UA_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage2 UA bidder documents")
class CompetitiveDialogueStage2UaBidDocumentResource(TenderUaBidDocumentResource):
    pass


@bid_financial_documents_resource(
    name='{}:Tender Bid Financial Documents'.format(STAGE_2_EU_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/financial_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder financial documents")
class CompetitiveDialogueStage2EUBidFinancialDocumentResource(TenderEUBidFinancialDocumentResource):
    pass


@bid_eligibility_documents_resource(
    name='{}:Tender Bid Eligibility Documents'.format(STAGE_2_EU_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder eligibility documents")
class CompetitiveDialogueStage2EUBidEligibilityDocumentResource(TenderEUBidEligibilityDocumentResource):
    pass


@bid_qualification_documents_resource(
    name='{}:Tender Bid Qualification Documents'.format(STAGE_2_EU_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents',
    path='/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder qualification documents")
class CompetitiveDialogueStage2EUBidQualificationDocumentResource(TenderEUBidQualificationDocumentResource):
    pass
