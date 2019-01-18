# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
    get_now
)
from openprocurement.tender.core.validation import (
    validate_lot_data, validate_patch_lot_data,
)

from openprocurement.tender.core.utils import (
    save_tender, optendersresource, apply_patch,
)

from openprocurement.tender.belowthreshold.validation import validate_lot_operation


@optendersresource(name='belowThreshold:Tender Lots',
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType='belowThreshold',
                   description="Tender lots")
class TenderLotResource(APIResource):

    @json_view(content_type="application/json", validators=(validate_lot_data, validate_lot_operation), permission='edit_tender')
    def collection_post(self):
        """Add a lot
        """
        tender = self.request.validated['tender']
        lot = self.request.validated['lot']
        lot.date = get_now()
        tender.lots.append(lot)
        if save_tender(self.request):
            self.LOGGER.info('Created tender lot {}'.format(lot.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_create'}, {'lot_id': lot.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('{}:Tender Lots'.format(tender.procurementMethodType), tender_id=tender.id, lot_id=lot.id)
            return {'data': lot.serialize("view")}

    @json_view(permission='view_tender')
    def collection_get(self):
        """Lots Listing
        """
        return {'data': [i.serialize("view") for i in self.request.validated['tender'].lots]}

    @json_view(permission='view_tender')
    def get(self):
        """Retrieving the lot
        """
        return {'data': self.request.context.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_lot_data, validate_lot_operation), permission='edit_tender')
    def patch(self):
        """Update of lot
        """
        if apply_patch(self.request, src=self.request.context.serialize()):
            self.LOGGER.info('Updated tender lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(permission='edit_tender', validators=(validate_lot_operation,))
    def delete(self):
        """Lot deleting
        """
        tender = self.request.validated['tender']
        lot = self.request.context
        res = lot.serialize("view")
        tender.lots.remove(lot)
        if save_tender(self.request):
            self.LOGGER.info('Deleted tender lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_delete'}))
            return {'data': res}
