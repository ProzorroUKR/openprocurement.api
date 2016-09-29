# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation import TenderCancellationResource
from openprocurement.tender.openua.utils import add_next_award


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

    def validate_cancellation(self, operation):
        if not super(TenderUaCancellationResource, self).validate_cancellation(operation):
            return
        tender = self.request.validated['tender']
        cancellation = self.request.validated['cancellation']
        if not cancellation.relatedLot and tender.lots:
            active_lots = [i.id for i in tender.lots if i.status == 'active']
            statuses = [set([i.status for i in tender.awards if i.lotID == lot_id]) for lot_id in active_lots]
            block_cancellation = any([not i.difference(set(['unsuccessful', 'cancelled'])) if i else False for i in statuses])
        elif cancellation.relatedLot and tender.lots or not cancellation.relatedLot and not tender.lots:
            statuses = set([i.status for i in tender.awards if i.lotID == cancellation.relatedLot])
            block_cancellation = not statuses.difference(set(['unsuccessful', 'cancelled'])) if statuses else False
        if block_cancellation:
            self.request.errors.add('body', 'data', 'Can\'t {} cancellation if all awards is unsuccessful'.format(operation))
            self.request.errors.status = 403
            return
        return True
