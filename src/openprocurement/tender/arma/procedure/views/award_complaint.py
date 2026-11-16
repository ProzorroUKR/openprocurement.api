from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
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
    procurementMethodType=ARMAProcurementMethodType,
    request_method=["GET"],
    description="Tender award complaints get",
)
class AwardClaimAndComplaintGetResource(BaseAwardComplaintGetResource):
    pass


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Claims",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ARMAProcurementMethodType,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender award claims",
)
class AwardClaimResource(BaseAwardClaimResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetAwardClaimState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetAwardClaimState,
    }


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType=ARMAProcurementMethodType,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender award complaints",
)
class AwardComplaintWriteResource(BaseAwardComplaintWriteResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetAwardComplaintState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetAwardComplaintState,
    }
