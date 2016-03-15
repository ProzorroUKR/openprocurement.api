# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource as TenderBidDocumentResource


@opresource(name='Tender UA.defense Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender UA.defense bidder documents")
class TenderUaBidDocumentResource(TenderBidDocumentResource):
    pass
