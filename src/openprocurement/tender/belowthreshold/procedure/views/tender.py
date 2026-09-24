from cornice.resource import resource

from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.belowthreshold.procedure.state.tender_details import (
    BelowThresholdTenderDetailsState,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{BELOW_THRESHOLD}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=BELOW_THRESHOLD,
    description="BelowThreshold tenders",
    accept="application/json",
)
class BelowThresholdTenderResource(TendersResource):
    state_class = BelowThresholdTenderDetailsState
