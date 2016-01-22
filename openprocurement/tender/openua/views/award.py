# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.api.views.award import TenderAwardResource

LOGGER = getLogger(__name__)


@opresource(name='Tender UA Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender awards",
            procurementMethodType='aboveThresholdUA')
class TenderUaAwardResource(TenderAwardResource):
    pass