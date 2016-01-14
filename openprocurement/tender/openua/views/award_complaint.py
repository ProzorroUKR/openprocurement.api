# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.views.award_complaint import TenderAwardComplaintResource
from openprocurement.api.utils import (
    opresource,
)


LOGGER = getLogger(__name__)


@opresource(name='Tender UA Award Complaints',
            collection_path='/tenders/{tender_id}/awards/{award_id}/complaints',
            path='/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender award complaints")
class TenderUaAwardComplaintResource(TenderAwardComplaintResource):
    pass