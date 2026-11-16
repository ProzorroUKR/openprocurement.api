from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.open.procedure.state.cancellation import (
    AboveThresholdEUCancellationState,
    AboveThresholdUACancellationState,
)


@resource(
    name="{}:Tender Cancellations".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue stage2 UE cancellations",
)
class CD2EUDefenseCancellationResource(BaseCancellationResource):
    state_class = AboveThresholdEUCancellationState


@resource(
    name="{}:Tender Cancellations".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue stage2 UA cancellations",
)
class CD2UADefenseCancellationResource(BaseCancellationResource):
    state_class = AboveThresholdUACancellationState
