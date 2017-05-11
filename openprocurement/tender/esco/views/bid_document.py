# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource


@opresource(name='Tender ESCO EU Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU bidder documents")
class TenderESCOEUBidDocumentResource(TenderEUBidDocumentResource):
    """ Tender ESCO EU Bid Document Resource """
