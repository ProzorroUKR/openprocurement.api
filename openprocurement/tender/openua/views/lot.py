# -*- coding: utf-8 -*-
from datetime import timedelta
from logging import getLogger
from openprocurement.api.views.lot import TenderLotResource

from openprocurement.api.utils import (
    apply_patch,
    save_tender,
    opresource,
    json_view,
    context_unpack
)
from openprocurement.api.validation import (
    validate_lot_data,
    validate_patch_lot_data,
)
from openprocurement.api.models import get_now
from openprocurement.tender.openua.utils import calculate_buisness_date

LOGGER = getLogger(__name__)



@opresource(name='Tender UA Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender Ua lots")
class TenderUaLotResource(TenderLotResource):

    def validate_update_tender(self, operation):
        tender = self.request.validated['tender']
        if tender.status not in ['active.tendering']:
            self.request.errors.add('body', 'data', 'Can\'t {} lot in current ({}) tender status'.format(operation, tender.status))
            self.request.errors.status = 403
            return
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            if calculate_buisness_date(get_now(), timedelta(days=4)) >= tender.enquiryPeriod.endDate:
                self.request.errors.add('body', 'data', 'enquiryPeriod should be extended by 4 days')
                self.request.errors.status = 403
                return
            elif calculate_buisness_date(get_now(), timedelta(days=7)) >= tender.tenderPeriod.endDate:
                self.request.errors.add('body', 'data', 'tenderPeriod should be extended by 7 days')
                self.request.errors.status = 403
                return
        return True

    @json_view(content_type="application/json", validators=(validate_lot_data,), permission='edit_tender')
    def collection_post(self):
        """Add a lot
        """
        if not self.validate_update_tender('add'):
            return
        lot = self.request.validated['lot']
        tender = self.request.validated['tender']
        tender.lots.append(lot)
        if save_tender(self.request):
            LOGGER.info('Created tender lot {}'.format(lot.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_create'}, {'lot_id': lot.id}))
            self.request.response.status = 201
            self.request.response.headers['Location'] = self.request.route_url('Tender UA Lots', tender_id=tender.id, lot_id=lot.id)
            return {'data': lot.serialize("view")}

    @json_view(content_type="application/json", validators=(validate_patch_lot_data,), permission='edit_tender')
    def patch(self):
        """Update of lot
        """
        if not self.validate_update_tender('update'):
            return
        if apply_patch(self.request, src=self.request.context.serialize()):
            LOGGER.info('Updated tender lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_patch'}))
            return {'data': self.request.context.serialize("view")}

    @json_view(permission='edit_tender')
    def delete(self):
        """Lot deleting
        """
        if not self.validate_update_tender('delete'):
            return
        lot = self.request.context
        res = lot.serialize("view")
        tender = self.request.validated['tender']
        tender.lots.remove(lot)
        if save_tender(self.request):
            LOGGER.info('Deleted tender lot {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_lot_delete'}))
            return {'data': res}
