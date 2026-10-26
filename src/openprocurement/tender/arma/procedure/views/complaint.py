from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.claim import (
    ComplexAssetClaimState,
    SimpleAssetClaimState,
)
from openprocurement.tender.arma.procedure.state.complaint import (
    ComplexAssetComplaintState,
    SimpleAssetComplaintState,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    request_method=["GET"],
    description="Tender complaints get",
)
class ClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class ClaimResource(TenderClaimResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetClaimState,
        SIMPLE_ASSET_ARMA: SimpleAssetClaimState,
    }


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class ComplaintResource(TenderComplaintResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetComplaintState,
        SIMPLE_ASSET_ARMA: SimpleAssetComplaintState,
    }
