from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource,
)


@resource(
    name="{}:Tender Qualification Complaint Appeal Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification complaint appeal documents",
)
class CDEUQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    pass


@resource(
    name="{}:Tender Qualification Complaint Appeal Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification complaint appeal documents",
)
class CDUAQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    pass
