from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage1.claim import (
    CDStage1TenderClaimState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.complaint import (
    CDStage1TenderComplaintState,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)


@resource(
    name="{}:Tender Complaints Get".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    request_method=["GET"],
    description="Competitive Dialogue EU complaints get",
)
class CDEUTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="{}:Tender Claims".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    request_method=["PATCH"],
    complaintType="claim",
    description="Competitive Dialogue EU claims",
)
class CDEUTenderClaimResource(TenderClaimResource):
    state_class = CDStage1TenderClaimState


@resource(
    name="{}:Tender Complaints".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue EU complaints",
)
class CDEUTenderComplaintResource(TenderComplaintResource):
    state_class = CDStage1TenderComplaintState


# CD UA


@resource(
    name="{}:Tender Complaints Get".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    request_method=["GET"],
    description="Competitive Dialogue UA complaints get",
)
class CDUATenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="{}:Tender Claims".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    request_method=["PATCH"],
    complaintType="claim",
    description="Competitive Dialogue UA claims",
)
class CDUATenderClaimResource(TenderClaimResource):
    state_class = CDStage1TenderClaimState


@resource(
    name="{}:Tender Complaints".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue UA complaints",
)
class CDUATenderComplaintResource(TenderComplaintResource):
    state_class = CDStage1TenderComplaintState
