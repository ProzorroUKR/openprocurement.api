from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource,
)


@resource(
    name="{}:Tender Qualification Complaint Appeals".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Tender qualification complaint appeals",
)
class CDEUQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    pass


@resource(
    name="{}:Tender Qualification Complaint Appeals".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Tender qualification complaint appeals",
)
class CDUAQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    pass
