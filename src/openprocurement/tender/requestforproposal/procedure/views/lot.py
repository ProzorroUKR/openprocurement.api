from cornice.resource import resource

from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.requestforproposal.procedure.state.lot import RFPTenderLotState


@resource(
    name="requestForProposal:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="requestForProposal",
    description="Tender lots",
)
class RequestForProposalTenderLotResource(TenderLotResource):
    state_class = RFPTenderLotState
