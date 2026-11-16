from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)
from openprocurement.tender.limited.procedure.state.cancellation import (
    NegotiationCancellationState,
    ReportingCancellationState,
)


@resource(
    name="reporting:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.REPORTING,
    description="Tender cancellations",
)
class ReportingCancellationResource(BaseCancellationResource):
    state_class = ReportingCancellationState


@resource(
    name="negotiation:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender cancellations",
)
class NegotiationCancellationResource(BaseCancellationResource):
    state_class = NegotiationCancellationState


@resource(
    name="negotiation.quick:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender cancellations",
)
class NegotiationQuickCancellationResource(NegotiationCancellationResource):
    pass
