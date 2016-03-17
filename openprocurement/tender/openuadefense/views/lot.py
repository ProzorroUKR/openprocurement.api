# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.lot import TenderUaLotResource as TenderLotResource
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
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import TENDERING_EXTRA_PERIOD


@opresource(name='Tender UA.defense Lots',
            collection_path='/tenders/{tender_id}/lots',
            path='/tenders/{tender_id}/lots/{lot_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender Ua lots")
class TenderUaLotResource(TenderLotResource):

    def validate_update_tender(self, operation):
        tender = self.request.validated['tender']
        if tender.status not in ['active.tendering']:
            self.request.errors.add('body', 'data', 'Can\'t {} lot in current ({}) tender status'.format(operation, tender.status))
            self.request.errors.status = 403
            return
        if calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, tender) > tender.tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} days'.format(TENDERING_EXTRA_PERIOD))
            self.request.errors.status = 403
            return
        return True
