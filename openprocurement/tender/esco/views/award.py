# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.award import TenderUaAwardResource
from openprocurement.tender.openeu.views.award import TenderAwardResource as TenderEUAwardResource


@opresource(name='Tender ESCO UA Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender ESCO UA Awards",
            procurementMethodType='esco.UA')
class TenderESCOUAAwardResource(TenderUaAwardResource):
    """ Tender ESCO UA Award Resource """


@opresource(name='Tender ESCO EU Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender ESCO EU Awards",
            procurementMethodType='esco.EU')
class TenderESCOEUAwardResource(TenderEUAwardResource):
    """ Tender ESCO EU Award Resource """
