from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_post import (
    BaseAwardComplaintPostResource,
)


@resource(
    name="negotiation:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender award complaint posts",
)
class NegotiationAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Complaint Posts",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/posts/{post_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender award complaint posts",
)
class NegotiationQuickAwardComplaintPostResource(BaseAwardComplaintPostResource):
    pass
