# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid_document import (
    TenderEUBidDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE, CD_UA_TYPE
)


@optendersresource(
    name='{}:Tender Bid Documents'.format(CD_EU_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU bidder documents")
class CompetitiveDialogueEUBidDocumentResource(TenderEUBidDocumentResource):
    pass


@optendersresource(
    name='{}:Tender Bid Documents'.format(CD_UA_TYPE),
    collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
    path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA bidder documents")
class CompetitiveDialogueUaBidDocumentResource(TenderEUBidDocumentResource):
    pass
