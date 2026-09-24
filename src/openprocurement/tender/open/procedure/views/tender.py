from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.tender_details import (
    OpenTenderDetailsState,
)


@resource(
    name=f"{ABOVE_THRESHOLD}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tenders",
    accept="application/json",
)
class AboveThresholdTenderResource(TendersResource):
    state_class = OpenTenderDetailsState
