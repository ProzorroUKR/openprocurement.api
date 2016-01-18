# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.cancellation import TenderCancellationResource as BaseResource


LOGGER = getLogger(__name__)


@opresource(name='TenderEU Cancellations',
            collection_path='/tenders/{tender_id}/cancellations',
            path='/tenders/{tender_id}/cancellations/{cancellation_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender cancellations")
class TenderCancellationResource(BaseResource):
    """ TenderEU Cancellations """
