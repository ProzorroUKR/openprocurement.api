from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)


@resource(
    name="complexAsset.arma:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender award complaint posts",
)
class AwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
