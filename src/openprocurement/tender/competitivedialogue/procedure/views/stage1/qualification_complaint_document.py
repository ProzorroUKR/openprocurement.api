from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_document import (
    QualificationComplaintDocumentResource,
)


@resource(
    name="{}:Tender Qualification Complaint Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU Qualification Complaint Documents",
)
class CDEUQualificationComplaintDocumentResource(QualificationComplaintDocumentResource):
    pass


@resource(
    name="{}:Tender Qualification Complaint Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA Qualification Complaint Documents",
)
class CDUAQualificationComplaintDocumentResource(QualificationComplaintDocumentResource):
    pass
