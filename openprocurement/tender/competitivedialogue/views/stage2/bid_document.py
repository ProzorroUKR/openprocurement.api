# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE


@opresource(
    name='Competitive Dialogue Stage2 EU Bid Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage2 EU bidder documents")
class CompetitiveDialogueStage2EUBidDocumentResource(TenderEUBidDocumentResource):
    pass


@opresource(
    name='Competitive Dialogue Stage2 UA Bid Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage2 UA bidder documents")
class CompetitiveDialogueStage2UaBidDocumentResource(TenderUaBidDocumentResource):
    pass
