# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    opresource,
    json_view,
    context_unpack,
    APIResource
)
from openprocurement.api.validation import (
    validate_cancellation_data,
    validate_patch_cancellation_data,
)
from openprocurement.api.views.cancellation import TenderCancellationResource


@opresource(name='Tender Limited Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='reporting',
            description="Tender cancellations")
class TenderReportingCancellationResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_cancellation_data,), permission='edit_tender')
    def collection_post(self):
        """Post a cancellation
        """
        tender = self.request.validated['tender']
        if tender.status in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t add cancellation in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        cancellation = self.request.validated['cancellation']
        cancellation.date = get_now()
        if cancellation.status == 'active':
            tender.status = 'cancelled'
        tender.cancellations.append(cancellation)
        if save_tender(self.request):
            self.LOGGER.info('Created tender cancellation {}'.format(cancellation.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_cancellation_create'}, {'cancellation_id': cancellation.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender Cancellations', tender_id=tender.id, cancellation_id=cancellation.id)
            return {'data': cancellation.serialize("view")}

    @json_view(permission='view_tender')
    def collection_get(self):
        """List cancellations
        """
        return {'data': [i.serialize("view") for i in self.request.validated['tender'].cancellations]}

    @json_view(permission='view_tender')
    def get(self):
        """Retrieving the cancellation
        """
        return {'data': self.request.validated['cancellation'].serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_cancellation_data,), permission='edit_tender')
    def patch(self):
        """Post a cancellation resolution
        """
        tender = self.request.validated['tender']
        if tender.status in ['complete', 'cancelled', 'unsuccessful']:
            self.request.errors.add('body', 'data', 'Can\'t update cancellation in current ({}) tender status'.format(tender.status))
            self.request.errors.status = 403
            return
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if self.request.context.status == 'active':
            tender.status = 'cancelled'
        if save_tender(self.request):
            self.LOGGER.info('Updated tender cancellation {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_cancellation_patch'}))
            return {'data': self.request.context.serialize("view")}


@opresource(name='Tender Negotiation Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='negotiation',
            description="Tender cancellations")
class TenderNegotiationCancellationResource(TenderCancellationResource):
    """ Tender Negotiation Cancellation Resource """

    def cancel_tender(self):
        tender = self.request.validated['tender']
        tender.status = 'cancelled'

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

    def validate_cancellation(self, operation):
        if not super(TenderNegotiationCancellationResource, self).validate_cancellation(operation):
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


@opresource(name='Tender Negotiation Quick Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='negotiation.quick',
            description="Tender cancellations")
class TenderNegotiationQuickCancellationResource(TenderNegotiationCancellationResource):
    """ Tender Negotiation Quick Cancellation Resource """
