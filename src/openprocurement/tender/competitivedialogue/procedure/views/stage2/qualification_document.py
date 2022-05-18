# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.views.qualification_document import BaseQualificationDocumentResource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Qualification Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU qualification documents",
)
class CompetitiveDialogueStage2QualificationDocumentResource(BaseQualificationDocumentResource):
    pass