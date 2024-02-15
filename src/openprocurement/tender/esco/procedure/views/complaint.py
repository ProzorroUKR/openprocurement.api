from cornice.resource import resource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.esco.procedure.state.claim import ESCOClaimState
from openprocurement.tender.esco.procedure.state.complaint import ESCOComplaintState


@resource(
    name="esco:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["GET"],
    description="Tender ESCO complaints get",
)
class ESCOTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="esco:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender ESCO Claims",
)
class ESCOTenderClaimResource(TenderClaimResource):
    state_class = ESCOClaimState


@resource(
    name="esco:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender ESCO Complaints",
)
class ESCOTenderComplaintResource(TenderComplaintResource):
    state_class = ESCOComplaintState
