# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.api.views.contract_document import TenderAwardContractDocumentResource


@opresource(name='Tender UA Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender contract documents")
class TenderUaAwardContractDocumentResource(TenderAwardContractDocumentResource):
    pass
