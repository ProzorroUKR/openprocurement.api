from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal import (
    CFAUAComplaintAppealState,
)
from openprocurement.tender.core.procedure.views.award_complaint_appeal import (
    BaseAwardComplaintAppealResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Award Complaint Appeals",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender award complaint appeals",
)
class CFAUAAwardComplaintAppealResource(BaseAwardComplaintAppealResource):
    state_class = CFAUAComplaintAppealState
