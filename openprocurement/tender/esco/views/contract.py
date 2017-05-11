# -*- coding: utf-8 -*-
from openprocurement.tender.openeu.views.contract import TenderAwardContractResource as TenderEUContractResource
from openprocurement.api.utils import opresource


@opresource(name='Tender ESCO EU Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU contracts")
class TenderESCOEUContractResource(TenderEUContractResource):
    """ Tender ESCO EU Contract Resource """
