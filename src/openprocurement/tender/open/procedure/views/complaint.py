from cornice.resource import resource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_GROUP_NAME, ABOVE_THRESHOLD_GROUP
from openprocurement.tender.open.procedure.state.claim import OpenTenderClaimState
from openprocurement.tender.open.procedure.state.complaint import OpenTenderComplaintState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    request_method=["GET"],
    description="Tender complaints get",
)
class OpenTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class OpenTenderClaimResource(TenderClaimResource):
    state_class = OpenTenderClaimState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class OpenTenderComplaintResource(TenderComplaintResource):
    state_class = OpenTenderComplaintState

