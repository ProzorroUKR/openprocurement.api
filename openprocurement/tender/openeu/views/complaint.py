# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.complaint import TenderUaComplaintResource

LOGGER = getLogger(__name__)


@opresource(name='Tender EU Complaints',
            collection_path='/tenders/{tender_id}/complaints',
            path='/tenders/{tender_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU complaints")
class TenderEUComplaintResource(TenderUaComplaintResource):
    pass
