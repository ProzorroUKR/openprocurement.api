# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.contract_document import TenderUaAwardContractDocumentResource as TenderAwardContractDocumentResource


@opresource(name='Tender UA.defense Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA.defense',
            description="Tender contract documents")
class TenderUaAwardContractDocumentResource(TenderAwardContractDocumentResource):
    """ """
