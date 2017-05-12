# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(name='esco.EU:Tender',
                   path='/tenders/{tender_id}',
                   procurementMethodType='esco.EU',
                   description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOEUResource(TenderEUResource):
    """ Resource handler for Tender ESCO EU """
