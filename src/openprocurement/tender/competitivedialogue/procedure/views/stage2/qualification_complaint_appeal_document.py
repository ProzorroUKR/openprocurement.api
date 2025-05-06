from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Qualification Complaint Appeal Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender qualification complaint appeal documents",
)
class CD2EUQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    pass
