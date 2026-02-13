from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.claim import ClaimState
from openprocurement.tender.arma.procedure.state.complaint import ComplaintState
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)


@resource(
    name="complexAsset.arma:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["GET"],
    description="Tender complaints get",
)
class ClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="complexAsset.arma:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class ClaimResource(TenderClaimResource):
    state_class = ClaimState


@resource(
    name="complexAsset.arma:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class ComplaintResource(TenderComplaintResource):
    state_class = ComplaintState
