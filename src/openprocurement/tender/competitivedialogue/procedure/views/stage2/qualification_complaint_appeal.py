from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource,
)


@resource(
    name="{}:Tender Qualification Complaint Appeals".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender qualification complaint appeals",
)
class CD2EUQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    pass
