from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.cancellation import (
    CFASelectionCancellationState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender cancellations",
)
class CFASelectionCancellationResource(BaseCancellationResource):
    state_class = CFASelectionCancellationState
