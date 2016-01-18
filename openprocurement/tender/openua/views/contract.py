# -*- coding: utf-8 -*-
from logging import getLogger
from openprocurement.api.models import get_now
from openprocurement.api.utils import opresource
from openprocurement.api.views.contract import TenderAwardContractResource


LOGGER = getLogger(__name__)


@opresource(name='Tender UA Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender contracts")
class TenderUaAwardContractResource(TenderAwardContractResource):
    pass
