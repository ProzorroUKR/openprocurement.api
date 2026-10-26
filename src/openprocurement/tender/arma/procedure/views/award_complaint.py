from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.award_claim import (
    ComplexAssetAwardClaimState,
    SimpleAssetAwardClaimState,
)
from openprocurement.tender.arma.procedure.state.award_complaint import (
    ComplexAssetAwardComplaintState,
    SimpleAssetAwardComplaintState,
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
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    request_method=["GET"],
    description="Tender award complaints get",
)
class AwardClaimAndComplaintGetResource(BaseAwardComplaintGetResource):
    pass


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class AwardClaimResource(BaseAwardClaimResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetAwardClaimState,
        SIMPLE_ASSET_ARMA: SimpleAssetAwardClaimState,
    }


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class AwardComplaintWriteResource(BaseAwardComplaintWriteResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetAwardComplaintState,
        SIMPLE_ASSET_ARMA: SimpleAssetAwardComplaintState,
    }
