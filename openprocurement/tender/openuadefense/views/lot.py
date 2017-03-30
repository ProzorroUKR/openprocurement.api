# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, error_handler
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.lot import (
    TenderUaLotResource as TenderLotResource
)
from openprocurement.tender.core.utils import calculate_business_date
from openprocurement.tender.openuadefense.constants import (
    TENDERING_EXTRA_PERIOD
)


@optendersresource(name='aboveThresholdUA.defense:Tender Lots',
                   collection_path='/tenders/{tender_id}/lots',
                   path='/tenders/{tender_id}/lots/{lot_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender Ua lots")
class TenderUaLotResource(TenderLotResource):

    def validate_update_tender(self):
        tender = self.request.validated['tender']
        if calculate_business_date(get_now(), TENDERING_EXTRA_PERIOD, tender, True) > tender.tenderPeriod.endDate:
            self.request.errors.add('body', 'data', 'tenderPeriod should be extended by {0.days} working days'.format(TENDERING_EXTRA_PERIOD))
            self.request.errors.status = 403
            raise error_handler(self.request.errors)
        return True
