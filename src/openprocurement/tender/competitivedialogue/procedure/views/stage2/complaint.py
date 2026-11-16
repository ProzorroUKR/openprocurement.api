from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.claim import (
    CDStage2EUTenderClaimState,
    CDStage2UATenderClaimState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.complaint import (
    CDStage2EUTenderComplaintState,
    CDStage2UATenderComplaintState,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)


@resource(
    name="{}:Tender Complaints Get".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    request_method=["GET"],
    description="Competitive Dialogue stage2 EU complaints get",
)
class CD2EUTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="{}:Tender Claims".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    request_method=["PATCH"],
    complaintType="claim",
    description="Competitive Dialogue stage2 EU claims",
)
class CD2EUTenderClaimResource(TenderClaimResource):
    state_class = CDStage2EUTenderClaimState


@resource(
    name="{}:Tender Complaints".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue stage2 EU complaints",
)
class CD2EUTenderComplaintResource(TenderComplaintResource):
    state_class = CDStage2EUTenderComplaintState


@resource(
    name="{}:Tender Complaints Get".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    request_method=["GET"],
    description="Competitive Dialogue stage2 UA complaints get",
)
class CD2UATenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="{}:Tender Claims".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    request_method=["PATCH"],
    complaintType="claim",
    description="Competitive Dialogue stage2 UA claims",
)
class CD2UATenderClaimResource(TenderClaimResource):
    state_class = CDStage2UATenderClaimState


@resource(
    name="{}:Tender Complaints".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue stage2 UA complaints",
)
class CD2UATenderComplaintResource(TenderComplaintResource):
    state_class = CDStage2UATenderComplaintState
