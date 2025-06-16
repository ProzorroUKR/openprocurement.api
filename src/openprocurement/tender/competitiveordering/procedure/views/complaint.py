from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.claim import (
    COTenderClaimState,
)
from openprocurement.tender.competitiveordering.procedure.state.complaint import (
    COTenderComplaintState,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    request_method=["GET"],
    description="Tender complaints get",
)
class COTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class COTenderClaimResource(TenderClaimResource):
    state_class = COTenderClaimState


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class COTenderComplaintResource(TenderComplaintResource):
    state_class = COTenderComplaintState
