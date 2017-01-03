# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.tender import TenderUAResource
from openprocurement.tender.openeu.views.tender import TenderEUResource
from openprocurement.tender.limited.views.tender import TenderResource as TenderReportingResource
from openprocurement.api.utils import opresource


@opresource(name='Tender ESCO UA',
            path='/tenders/{tender_id}',
            procurementMethodType='ecso.UA',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOUAResource(TenderUAResource):
    """ Resource handler for Tender ESCO UA """


@opresource(name='Tender ESCO EU',
            path='/tenders/{tender_id}',
            procurementMethodType='ecso.EU',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOEUResource(TenderEUResource):
    """ Resource handler for Tender ESCO EU """


@opresource(name='Tender ESCO Reporting',
            path='/tenders/{tender_id}',
            procurementMethodType='ecso.reporting',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderESCOReportingResource(TenderReportingResource):
    """ Resource handler for Tender ESCO Reporting """
