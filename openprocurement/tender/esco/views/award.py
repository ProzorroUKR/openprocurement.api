# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.award import TenderUaAwardResource
from openprocurement.tender.openeu.views.award import TenderAwardResource as TenderEUAwardResource


@optendersresource(name='Tender ESCO UA Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender ESCO UA Awards",
            procurementMethodType='esco.UA')
class TenderESCOUAAwardResource(TenderUaAwardResource):
    """ Tender ESCO UA Award Resource """


@optendersresource(name='Tender ESCO EU Awards',
            collection_path='/tenders/{tender_id}/awards',
            path='/tenders/{tender_id}/awards/{award_id}',
            description="Tender ESCO EU Awards",
            procurementMethodType='esco.EU')
class TenderESCOEUAwardResource(TenderEUAwardResource):
    """ Tender ESCO EU Award Resource """
