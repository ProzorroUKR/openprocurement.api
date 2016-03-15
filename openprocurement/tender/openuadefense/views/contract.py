# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.contract import TenderUaAwardContractResource as TenderAwardContractResource


@opresource(name='Tender UA.defense Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender contracts")
class TenderUaAwardContractResource(TenderAwardContractResource):
    """ """
