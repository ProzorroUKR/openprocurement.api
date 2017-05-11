# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.contract_document import TenderAwardContractDocumentResource as TenderEUContractDocumentResource


@opresource(name='Tender ESCO EU Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Contract documents")
class TenderESCOEUContractDocumentResource(TenderEUContractDocumentResource):
    """ Tender EU Contract Document Resource """
