# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view, context_unpack, APIResource, get_now, raise_operation_error
)

from openprocurement.tender.core.utils import (
    apply_patch, save_tender, optendersresource
)

from openprocurement.tender.core.validation import (
    validate_cancellation_data, validate_patch_cancellation_data,
)

from openprocurement.tender.belowthreshold.views.cancellation import (
    TenderCancellationResource
)

from openprocurement.tender.limited.validation import validate_cancellation_in_termainated_status


@optendersresource(name='reporting:Tender Cancellations',
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType='reporting',
                   description="Tender cancellations")
class TenderReportingCancellationResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_cancellation_data, validate_cancellation_in_termainated_status), permission='edit_tender')
    def collection_post(self):
        """Post a cancellation
        """
        tender = self.request.validated['tender']
        cancellation = self.request.validated['cancellation']
        cancellation.date = get_now()
        if cancellation.status == 'active':
            tender.status = 'cancelled'
        tender.cancellations.append(cancellation)
        if save_tender(self.request):
            self.LOGGER.info('Created tender cancellation {}'.format(cancellation.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_cancellation_create'}, {'cancellation_id': cancellation.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('{}:Tender Cancellations'.format(tender.procurementMethodType),
                                                                               tender_id=tender.id, cancellation_id=cancellation.id)
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

    @json_view(content_type="application/json", validators=(validate_patch_cancellation_data, validate_cancellation_in_termainated_status), permission='edit_tender')
    def patch(self):
        """Post a cancellation resolution
        """
        tender = self.request.validated['tender']
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if self.request.context.status == 'active':
            tender.status = 'cancelled'
        if save_tender(self.request):
            self.LOGGER.info('Updated tender cancellation {}'.format(self.request.context.id),
                             extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_cancellation_patch'}))
            return {'data': self.request.context.serialize("view")}


@optendersresource(name='negotiation:Tender Cancellations',
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType='negotiation',
                   description="Tender cancellations")
class TenderNegotiationCancellationResource(TenderCancellationResource):
    """ Tender Negotiation Cancellation Resource """

    def validate_cancellation(self, operation):
        """ TODO move validators
        This class is inherited from below package, but validate_cancellation function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if not super(TenderNegotiationCancellationResource, self).validate_cancellation(operation):
            return
        tender = self.request.validated['tender']
        cancellation = self.request.validated['cancellation']
        if tender.lots:
            if not cancellation.relatedLot:
                if [lot for lot in tender.lots if lot.status == 'complete']:
                    raise_operation_error(self.request, 'Can\'t {} cancellation, if there is at least one complete lot'.format(operation))
        return True


@optendersresource(name='negotiation.quick:Tender Cancellations',
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType='negotiation.quick',
                   description="Tender cancellations")
class TenderNegotiationQuickCancellationResource(TenderNegotiationCancellationResource):
    """ Tender Negotiation Quick Cancellation Resource """
