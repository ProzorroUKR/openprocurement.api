from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_PROCUREMENT_METHOD_TYPES, ARMA_ROUTE_PREFIX
from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender award complaint posts",
)
class AwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
