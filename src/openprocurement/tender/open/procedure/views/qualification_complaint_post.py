from cornice.resource import resource

from openprocurement.tender.core.procedure.views.qualification_complaint_post import QualificationComplaintPostResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_EU, OPEN_ROUTE_PREFIX


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Qualification Complaint Posts",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    description="Tender qualification complaint posts",
    procurementMethodType=[ABOVE_THRESHOLD_EU],
)
class OpenQualificationComplaintPostResource(QualificationComplaintPostResource):
    pass
