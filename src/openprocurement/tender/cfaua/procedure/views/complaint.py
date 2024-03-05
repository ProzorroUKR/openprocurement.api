from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.claim import CFAUATenderClaimState
from openprocurement.tender.cfaua.procedure.state.complaint import (
    CFAUATenderComplaintState,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Complaints Get",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["GET"],
    description="Tender EU complaints get",
)
class CFAUATenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="closeFrameworkAgreementUA:Tender Claims",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["PATCH"],
    complaintType="claim",
    description="Tender EU claims",
)
class CFAUATenderClaimResource(TenderClaimResource):
    state_class = CFAUATenderClaimState


@resource(
    name="closeFrameworkAgreementUA:Tender Complaints",
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender EU complaints",
)
class CFAUATenderComplaintResource(TenderComplaintResource):
    state_class = CFAUATenderComplaintState
