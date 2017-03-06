# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.lot import (
    TenderUaLotResource as TenderLotResource
)
from openprocurement.tender.openuadefense.utils import calculate_business_date
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD
)


@optendersresource(name='aboveThresholdUA.defense:Tender Lots',
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
        if calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, tender, True) > tender.tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} working days'.format(TENDERING_EXTRA_PERIOD))
            self.request.errors.status = 403
            return
        return True
