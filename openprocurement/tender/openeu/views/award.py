# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award import TenderUaAwardResource as BaseResource


@optendersresource(name='aboveThresholdEU:Tender Awards',
                   collection_path='/tenders/{tender_id}/awards',
                   path='/tenders/{tender_id}/awards/{award_id}',
                   description="Tender EU awards",
                   procurementMethodType='aboveThresholdEU')
class TenderAwardResource(BaseResource):
    """ EU award resource """
