# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.cancellation import (
    TenderUaCancellationResource as TenderCancellationResource
)


@optendersresource(name='aboveThresholdUA.defense:Tender Cancellations',
                   collection_path='/tenders/{tender_id}/cancellations',
                   path='/tenders/{tender_id}/cancellations/{cancellation_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender cancellations")
class TenderUaCancellationResource(TenderCancellationResource):
    """ """
