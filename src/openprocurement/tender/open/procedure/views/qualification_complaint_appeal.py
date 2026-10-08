from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_complaint_appeal import (
    QualificationComplaintAppealResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_EU, OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaint Appeals",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    description="Tender qualification complaint appeals",
    procurementMethodType=[ABOVE_THRESHOLD_EU],
)
class OpenQualificationComplaintAppealResource(QualificationComplaintAppealResource):
    pass
