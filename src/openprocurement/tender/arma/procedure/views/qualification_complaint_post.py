from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.qualification_complaint_post import (
    QualificationComplaintPostResource as BaseQualificationComplaintPostResource,
)


@resource(
    name="complexAsset.arma:Tender Qualification Complaint Posts",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender qualification complaint posts",
)
class QualificationComplaintPostResource(BaseQualificationComplaintPostResource):
    pass
