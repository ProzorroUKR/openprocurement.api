# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource

LOGGER = getLogger(__name__)

from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource


@opresource(name='Tender EU Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU bidder documents")
class TenderEUBidDocumentResource(TenderUaBidDocumentResource):
    pass
