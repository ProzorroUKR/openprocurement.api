# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation import TenderCancellationResource
from openprocurement.tender.openua.utils import add_next_award

LOGGER = getLogger(__name__)


@opresource(name='Tender UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender cancellations")
class TenderUaCancellationResource(TenderCancellationResource):

    def cancel_lot(self, cancellation=None):
        if not cancellation:
            cancellation = self.context
        tender = self.request.validated['tender']
        [setattr(i, 'status', 'cancelled') for i in tender.lots if i.id == cancellation.relatedLot]
        statuses = set([lot.status for lot in tender.lots])
        if statuses == set(['cancelled']):
            self.cancel_tender()
        elif not statuses.difference(set(['unsuccessful', 'cancelled'])):
            tender.status = 'unsuccessful'
        elif not statuses.difference(set(['complete', 'unsuccessful', 'cancelled'])):
            tender.status = 'complete'
        if tender.status == 'active.auction' and all([
            i.auctionPeriod and i.auctionPeriod.endDate
            for i in self.request.validated['tender'].lots
            if i.status == 'active'
        ]):
            add_next_award(self.request)
