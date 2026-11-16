from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name="{}:Tender Qualification Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    description="Competitive Dialogue EU Qualification Documents",
)
class CompetitiveDialogueEUQualificationDocumentResource(BaseQualificationDocumentResource):
    pass


@resource(
    name="{}:Tender Qualification Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    description="Competitive Dialogue UA Qualification Documents",
)
class CompetitiveDialogueUAQualificationDocumentResource(BaseQualificationDocumentResource):
    pass
