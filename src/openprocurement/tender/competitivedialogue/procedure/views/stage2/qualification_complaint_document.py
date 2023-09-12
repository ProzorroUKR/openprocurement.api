from openprocurement.tender.core.procedure.views.qualification_complaint_document import (
    QualificationComplaintDocumentResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from cornice.resource import resource


@resource(
    name="{}:Tender Qualification Complaint Documents".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU qualification complaint documents",
)
class CD2EUQualificationComplaintDocumentResource(QualificationComplaintDocumentResource):
    pass
