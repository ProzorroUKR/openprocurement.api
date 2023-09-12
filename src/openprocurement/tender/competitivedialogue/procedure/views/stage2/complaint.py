from cornice.resource import resource
from openprocurement.tender.core.procedure.views.complaint import (
    BaseTenderComplaintGetResource,
    TenderComplaintResource,
)
from openprocurement.tender.core.procedure.views.claim import TenderClaimResource
from openprocurement.tender.openua.procedure.state.claim import OpenUAClaimState
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@resource(
    name="{}:Tender Complaints Get".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue stage2 EU complaints get",
)
class CD2EUTenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="{}:Tender Claims".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue stage2 EU claims",
)
class CD2EUTenderClaimResource(TenderClaimResource):
    state_class = OpenUAClaimState


@resource(
    name="{}:Tender Complaints".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue stage2 EU complaints",
)
class CD2EUTenderComplaintResource(TenderComplaintResource):
    pass


@resource(
    name="{}:Tender Complaints Get".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["GET"],
    description="Competitive Dialogue stage2 UA complaints get",
)
class CD2UATenderClaimAndComplaintGetResource(BaseTenderComplaintGetResource):
    pass


@resource(
    name="{}:Tender Claims".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="claim",
    description="Competitive Dialogue stage2 UA claims",
)
class CD2UATenderClaimResource(TenderClaimResource):
    state_class = OpenUAClaimState


@resource(
    name="{}:Tender Complaints".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/complaints",
    path="/tenders/{tender_id}/complaints/{complaint_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Competitive Dialogue stage2 UA complaints",
)
class CD2UATenderComplaintResource(TenderComplaintResource):
    pass

