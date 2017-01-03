# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.contract_document import TenderUaAwardContractDocumentResource as TenderUaContractDocumentResource
from openprocurement.tender.openeu.views.contract_document import TenderAwardContractDocumentResource as TenderEUContractDocumentResource
from openprocurement.tender.limited.views.contract_document import TenderAwardContractDocumentResource as TenderReportingContractDocumentResource


@opresource(name='Tender ESCO UA Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='esco.UA',
            description="Tender ESCO UA Contract documents")
class TenderESCOUAContractDocumentResource(TenderUaContractDocumentResource):
    """ Tender UA Contract Document Resource """


@opresource(name='Tender ESCO EU Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='esco.EU',
            description="Tender ESCO EU Contract documents")
class TenderESCOEUContractDocumentResource(TenderEUContractDocumentResource):
    """ Tender EU Contract Document Resource """


@opresource(name='Tender ESCO Reporting Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='esco.reporting',
            description="Tender ESCO Reporting Contract documents")
class TenderESCOReportingContractDocumentResource(TenderReportingContractDocumentResource):
    """ Tender Reporting Contract Document Resource """
