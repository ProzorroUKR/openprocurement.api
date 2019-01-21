# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract import (
    TenderUaAwardContractResource as BaseResource
)


@optendersresource(name='aboveThresholdEU:Tender Contracts',
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType='aboveThresholdEU',
                   description="Tender EU contracts")
class TenderAwardContractResource(BaseResource):
    """ """
