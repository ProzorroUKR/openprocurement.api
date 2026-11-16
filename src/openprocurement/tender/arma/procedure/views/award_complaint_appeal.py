from cornice.resource import resource

from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender award complaint appeals",
)
class AwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    pass
