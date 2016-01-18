# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.views.tender import TenderResource
from openprocurement.api.utils import opresource

LOGGER = getLogger(__name__)


@opresource(name='TenderEU',
            path='/tenders/{tender_id}',
            procurementMethodType='aboveThresholdEU',
            description="Open Contracting compatible data exchange format. See http://ocds.open-contracting.org/standard/r/master/#tender for more info")
class TenderEUResource(TenderResource):
    """ Resource handler for TenderEU """
