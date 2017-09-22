# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.openua.views.contract_document import (
    TenderUaAwardContractDocumentResource
)
from openprocurement.tender.openeu.views.contract_document import (
    TenderAwardContractDocumentResource as TenderEUAwardContractDocumentResource
)
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
)

@optendersresource(name='{}:Tender Contract Documents'.format(STAGE_2_EU_TYPE),
                   collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
                   path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_EU_TYPE,
                   description="Competitive Dialogue Stage 2 EU contract documents")
class CompetitiveDialogueStage2EUAwardContractDocumentResource(TenderEUAwardContractDocumentResource):
    pass


@optendersresource(name='{}:Tender Contract Documents'.format(STAGE_2_UA_TYPE),
                   collection_path='/tenders/{tender_id}/contracts/{contract_id}/documents',
                   path='/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}',
                   procurementMethodType=STAGE_2_UA_TYPE,
                   description="Competitive Dialogue Stage 2 UA contract documents")
class CompetitiveDialogueStage2UAAwardContractDocumentResource(TenderUaAwardContractDocumentResource):
    pass
