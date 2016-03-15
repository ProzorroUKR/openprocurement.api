# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.cancellation import TenderUaCancellationResource as TenderCancellationResource


@opresource(name='Tender UA.defense Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender cancellations")
class TenderUaCancellationResource(TenderCancellationResource):
    """ """
