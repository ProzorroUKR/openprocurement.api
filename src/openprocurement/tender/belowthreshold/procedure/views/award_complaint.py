from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.award_claim import (
    BelowThresholdAwardClaimState,
)
from openprocurement.tender.core.procedure.serializers.complaint import (
    ComplaintSerializer,
)
from openprocurement.tender.core.procedure.views.award_claim import AwardClaimResource
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
)


@resource(
    name="belowThreshold:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["GET"],
    description="Tender award complaints get",
)
class BelowThresholdAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    serializer_class = ComplaintSerializer


@resource(
    name="belowThreshold:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="belowThreshold",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class BelowThresholdAwardClaimResource(AwardClaimResource):
    state_class = BelowThresholdAwardClaimState
