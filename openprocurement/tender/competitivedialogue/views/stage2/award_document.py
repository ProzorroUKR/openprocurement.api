# -*- coding: utf-8 -*-
from openprocurement.tender.openua.views.award_document import TenderUaAwardDocumentResource
from openprocurement.tender.openeu.views.award_document import TenderAwardDocumentResource as TenderEUAwardDocumentResource
from openprocurement.tender.competitivedialogue.models import STAGE_2_UA_TYPE, STAGE_2_EU_TYPE
from openprocurement.api.utils import opresource


@opresource(name='Competitive Dialogue Stage 2 EU Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_EU_TYPE,
            description="Tender award documents")
class CompetitiveDialogueStage2EUAwardDocumentResource(TenderEUAwardDocumentResource):
    pass


@opresource(name='Competitive Dialogue Stage 2 UA Award Documents',
            collection_path='/tenders/{tender_id}/awards/{award_id}/documents',
            path='/tenders/{tender_id}/awards/{award_id}/documents/{document_id}',
            procurementMethodType=STAGE_2_UA_TYPE,
            description="Competitive Dialogue Stage 2 UA award documents")
class CompetitiveDialogueStage2UAAwardDocumentResource(TenderUaAwardDocumentResource):
    pass

