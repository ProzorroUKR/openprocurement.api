from cornice.resource import resource

from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.openeu.procedure.state.claim import OpenEUTenderClaimState
from openprocurement.tender.openeu.procedure.state.complaint import (
    OpenEUTenderComplaintState,
)


@resource(
    name="aboveThresholdEU:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["GET"],
    description="Tender EU complaints get",
)
class OpenEUTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="aboveThresholdEU:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender EU claims",
)
class OpenEUTenderClaimResource(TenderClaimResource):
    state_class = OpenEUTenderClaimState


@resource(
    name="aboveThresholdEU:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU complaints",
)
class OpenEUTenderComplaintResource(TenderComplaintResource):
    state_class = OpenEUTenderComplaintState
