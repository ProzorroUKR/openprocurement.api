# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.bid_document import TenderEUBidDocumentResource


@optendersresource(name='esco.EU:Tender Bid Documents',
                   collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
                   path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
                   procurementMethodType='esco.EU',
                   description="Tender ESCO EU bidder documents")
class TenderESCOEUBidDocumentResource(TenderEUBidDocumentResource):
    """ Tender ESCO EU Bid Document Resource """
