# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.contract import TenderUaAwardContractResource as TenderUaContractResource
from openprocurement.tender.openeu.views.contract import TenderAwardContractResource as TenderEUContractResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(name='Tender ESCO UA Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA contracts")
class TenderESCOUAContractResource(TenderUaContractResource):
    """ Tender ESCO UA Contract Resource """


@optendersresource(name='Tender ESCO EU Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU contracts")
class TenderESCOEUContractResource(TenderEUContractResource):
    """ Tender ESCO EU Contract Resource """
