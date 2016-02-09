# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource, json_view

LOGGER = getLogger(__name__)

from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource


@opresource(name='Tender EU Bid Documents',
            collection_path='/tenders/{tender_id}/bids/{bid_id}/documents',
            path='/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU bidder documents")
class TenderEUBidDocumentResource(TenderUaBidDocumentResource):

    @json_view(permission='view_tender')
    def collection_get(self):
        """Tender Bid Documents List"""
        if self.request.validated['tender_status'] == 'active.tendering' and self.request.authenticated_role != 'bid_owner':
            self.request.errors.add('body', 'data', 'Can\'t view bid documents in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        if self.request.params.get('all', ''):
            collection_data = [i.serialize("view") for i in self.context.documents]
        else:
            collection_data = sorted(dict([
                (i.id, i.serialize("view"))
                for i in self.context.documents
            ]).values(), key=lambda i: i['dateModified'])
        return {'data': collection_data}
