# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.tender import TenderUAResource
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.api.utils import opresource


@opresource(name='Tender ESCO UA',
            path='/tenders/{tender_id}',
            procurementMethodType='esco.UA',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOUAResource(TenderUAResource):
    """ Resource handler for Tender ESCO UA """


@opresource(name='Tender ESCO EU',
            path='/tenders/{tender_id}',
            procurementMethodType='esco.EU',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOEUResource(TenderEUResource):
    """ Resource handler for Tender ESCO EU """
