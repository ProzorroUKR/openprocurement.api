from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.award_claim import AwardClaimState
from openprocurement.tender.arma.procedure.state.award_complaint import (
    AwardComplaintState,
)
from openprocurement.tender.core.procedure.views.award_claim import (
    AwardClaimResource as BaseAwardClaimResource,
)
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource as BaseAwardComplaintGetResource,
)
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintWriteResource as BaseAwardComplaintWriteResource,
)


@resource(
    name="complexAsset.arma:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["GET"],
    description="Tender award complaints get",
)
class AwardClaimAndComplaintGetResource(BaseAwardComplaintGetResource):
    pass


@resource(
    name="complexAsset.arma:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class AwardClaimResource(BaseAwardClaimResource):
    state_class = AwardClaimState


@resource(
    name="complexAsset.arma:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class AwardComplaintWriteResource(BaseAwardComplaintWriteResource):
    state_class = AwardComplaintState
