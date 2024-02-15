from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_post_document import (
    QualificationComplaintPostDocumentResource,
)


@resource(
    name="{}:Tender Qualification Complaint Post Documents".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification complaint post documents",
)
class CDEUQualificationComplaintPostDocumentResource(QualificationComplaintPostDocumentResource):
    pass


@resource(
    name="{}:Tender Qualification Complaint Post Documents".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification complaint post documents",
)
class CDUAQualificationComplaintPostDocumentResource(QualificationComplaintPostDocumentResource):
    pass
