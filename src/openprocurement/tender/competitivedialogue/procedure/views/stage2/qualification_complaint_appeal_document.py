from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Qualification Complaint Appeal Documents".format(
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2
    ),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Tender qualification complaint appeal documents",
)
class CD2EUQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    pass
