# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openua.views.contract_document import TenderUaAwardContractDocumentResource
from openprocurement.tender.openeu.views.contract_document import TenderAwardContractDocumentResource as TenderEUAwardContractDocumentResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE


@opresource(name='Competitive Dialogue Stage 2 EU Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU contract documents")
class CompetitiveDialogueStage2EUAwardContractDocumentResource(TenderEUAwardContractDocumentResource):
    pass


@opresource(name='Competitive Dialogue Stage 2 UA Contract Documents',
            collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
            path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA contract documents")
class CompetitiveDialogueStage2UAAwardContractDocumentResource(TenderUaAwardContractDocumentResource):
    pass



