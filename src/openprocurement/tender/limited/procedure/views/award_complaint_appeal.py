from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name="negotiation:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender award complaint appeals",
)
class NegotiationAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender award complaint appeals",
)
class NegotiationQuickAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
