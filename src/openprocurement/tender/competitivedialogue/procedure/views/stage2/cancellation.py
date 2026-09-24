from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.cancellation import BaseCancellationResource
from openprocurement.tender.open.procedure.state.cancellation import (
    AboveThresholdEUCancellationState,
    AboveThresholdUACancellationState,
)


@resource(
    name="{}:Tender Cancellations".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue stage2 UE cancellations",
)
class CD2EUDefenseCancellationResource(BaseCancellationResource):
    state_class = AboveThresholdEUCancellationState


@resource(
    name="{}:Tender Cancellations".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue stage2 UA cancellations",
)
class CD2UADefenseCancellationResource(BaseCancellationResource):
    state_class = AboveThresholdUACancellationState
