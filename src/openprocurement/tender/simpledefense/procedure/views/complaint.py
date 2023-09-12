from cornice.resource import resource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource


@resource(
    name="simple.defense:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["GET"],
    description="Tender complaints get",
)
class SimpleDefenseTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="simple.defense:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Tender claims",
)
class SimpleDefenseTenderClaimResource(TenderClaimResource):
    pass


@resource(
    name="simple.defense:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender complaints",
)
class SimpleDefenseTenderComplaintResource(TenderComplaintResource):
    pass

