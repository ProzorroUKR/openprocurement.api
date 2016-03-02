# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.api.views.bid_document import TenderBidDocumentResource


@opresource(name='Tender UA Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender UA bidder documents")
class TenderUaBidDocumentResource(TenderBidDocumentResource):
    pass
