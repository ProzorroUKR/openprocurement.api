# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource
from openprocurement.tender.competitivedialogue.models import CD_EU_TYPE, CD_UA_TYPE


@opresource(
    name='Competitive Dialogue EU Bid Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder documents")
class CompetitiveDialogueEUBidDocumentResource(TenderEUBidDocumentResource):
    pass


@opresource(
    name='Competitive Dialogue UA Bid Documents',
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bidder documents")
class CompetitiveDialogueUaBidDocumentResource(TenderEUBidDocumentResource):
    pass
