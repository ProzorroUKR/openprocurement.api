# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.contract import TenderUaAwardContractResource as BaseResource


@opresource(name='Tender EU Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='aboveThresholdEU',
            description="Tender EU contracts")
class TenderAwardContractResource(BaseResource):
    """ """
