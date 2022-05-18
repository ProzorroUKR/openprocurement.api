# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.views.qualification_document import BaseQualificationDocumentResource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Qualification Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification Documents",
)
class CompetitiveDialogueEUQualificationDocumentResource(BaseQualificationDocumentResource):
    pass


@resource(
    name="{}:Tender Qualification Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification Documents",
)
class CompetitiveDialogueUAQualificationDocumentResource(BaseQualificationDocumentResource):
    pass