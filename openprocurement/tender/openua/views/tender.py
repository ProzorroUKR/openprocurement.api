# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.api.views.tender import TenderResource


@opresource(name='TenderUA',
            path='/tenders/{tender_id}',
            procurementMethodType='aboveThresholdUA',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderUAResource(TenderResource):
    """ Resource handler for TenderUA """


