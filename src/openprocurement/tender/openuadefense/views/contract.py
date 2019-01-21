# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract import (
    TenderUaAwardContractResource as TenderAwardContractResource
)


@optendersresource(name='aboveThresholdUA.defense:Tender Contracts',
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType='aboveThresholdUA.defense',
                   description="Tender contracts")
class TenderUaAwardContractResource(TenderAwardContractResource):
    """ """
