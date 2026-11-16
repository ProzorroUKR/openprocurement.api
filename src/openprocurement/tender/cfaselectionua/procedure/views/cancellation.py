from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
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
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA,
    description="Tender cancellations",
)
class CFASelectionCancellationResource(BaseCancellationResource):
    state_class = CFASelectionCancellationState
