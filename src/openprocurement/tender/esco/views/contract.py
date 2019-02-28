# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openeu.views.contract import \
    TenderAwardContractResource as TenderEUContractResource


@optendersresource(name='esco:Tender Contracts',
                   collection_path='/tenders/{tender_id}/contracts',
                   path='/tenders/{tender_id}/contracts/{contract_id}',
                   procurementMethodType='esco',
                   description="Tender ESCO contracts")
class TenderESCOContractResource(TenderEUContractResource):
    """ Tender ESCO Contract Resource """
