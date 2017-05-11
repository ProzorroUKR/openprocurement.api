# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract_document import TenderUaAwardContractDocumentResource as TenderUaContractDocumentResource
from openprocurement.tender.openeu.views.contract_document import TenderAwardContractDocumentResource as TenderEUContractDocumentResource


@optendersresource(name='Tender ESCO UA Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA Contract documents")
class TenderESCOUAContractDocumentResource(TenderUaContractDocumentResource):
    """ Tender UA Contract Document Resource """


@optendersresource(name='Tender ESCO EU Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Contract documents")
class TenderESCOEUContractDocumentResource(TenderEUContractDocumentResource):
    """ Tender EU Contract Document Resource """
