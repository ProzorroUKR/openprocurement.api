# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource as TenderBidDocumentResource


@optendersresource(name='aboveThresholdUA.defense:Tender Bid Documents',
                   collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
                   path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender UA.defense bidder documents")
class TenderUaBidDocumentResource(TenderBidDocumentResource):
    pass
