# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation import TenderCancellationResource

LOGGER = getLogger(__name__)


@opresource(name='Tender UA Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender cancellations")
class TenderUaCancellationResource(TenderCancellationResource):
    pass
