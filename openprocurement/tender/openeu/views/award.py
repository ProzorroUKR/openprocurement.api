# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award import TenderUaAwardResource as BaseResource

@opresource(name='Tender EU Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender EU awards",
            procurementMethodType='aboveThresholdEU')
class TenderAwardResource(BaseResource):
    """ EU award resource """
