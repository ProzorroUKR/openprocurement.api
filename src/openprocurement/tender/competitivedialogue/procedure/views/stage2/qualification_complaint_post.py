from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE
from openprocurement.tender.core.procedure.views.qualification_complaint_post import (
    QualificationComplaintPostResource,
)


@resource(
    name="{}:Tender Qualification Complaint Posts".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender qualification complaint posts",
)
class CD2EUQualificationComplaintPostResource(QualificationComplaintPostResource):
    pass
