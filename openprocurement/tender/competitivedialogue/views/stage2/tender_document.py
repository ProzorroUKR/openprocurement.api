# -*- coding: utf-8 -*-
from openprocurement.api.utils import opresource
from openprocurement.tender.openeu.views.tender_document import TenderEUDocumentResource
from openprocurement.tender.openua.views.tender_document import TenderUaDocumentResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE


@opresource(name='Competitive Dialogue Stage 2 EU Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Competitive Dialogue Stage 2 EU related binary files (PDFs, etc.)")
class CompetitiveDialogueStage2EUDocumentResource(TenderEUDocumentResource):
    pass


@opresource(name='Competitive Dialogue Stage 2 UA Documents',
            collection_path='/tenders/{tender_id}/documents',
            path='/tenders/{tender_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA related binary files (PDFs, etc.)")
class CompetitiveDialogueStage2UADocumentResource(TenderUaDocumentResource):
    pass
