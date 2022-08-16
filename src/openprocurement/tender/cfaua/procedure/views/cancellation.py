from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.cfaua.procedure.state.cancellation import CFAUACancellationState
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender cancellations",
)
class CFAUACancellationResource(BaseCancellationResource):
    state_class = CFAUACancellationState
