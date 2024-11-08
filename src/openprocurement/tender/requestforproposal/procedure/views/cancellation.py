from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)
from openprocurement.tender.requestforproposal.procedure.state.cancellation import (
    RequestForProposalCancellationState,
)


@resource(
    name="requestForProposal:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="requestForProposal",
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_class = RequestForProposalCancellationState
