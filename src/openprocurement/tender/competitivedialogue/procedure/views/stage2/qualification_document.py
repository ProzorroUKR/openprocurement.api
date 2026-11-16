from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_document import (
    BaseQualificationDocumentResource,
)


@resource(
    name="{}:Tender Qualification Documents".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU qualification documents",
)
class CompetitiveDialogueStage2QualificationDocumentResource(BaseQualificationDocumentResource):
    pass
