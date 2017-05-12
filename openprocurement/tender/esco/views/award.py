# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.award import TenderAwardResource as TenderEUAwardResource


@optendersresource(name='esco.EU:Tender Awards',
                   collection_path='/tenders/{tender_id}/awards',
                   path='/tenders/{tender_id}/awards/{award_id}',
                   description="Tender ESCO EU Awards",
                   procurementMethodType='esco.EU')
class TenderESCOEUAwardResource(TenderEUAwardResource):
    """ Tender ESCO EU Award Resource """
