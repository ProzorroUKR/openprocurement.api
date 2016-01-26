# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.views.complaint import TenderComplaintResource
from openprocurement.api.utils import opresource

LOGGER = getLogger(__name__)


@opresource(name='Tender EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU complaints")
class TenderComplaintResource(TenderComplaintResource):
    """  TODO  """
