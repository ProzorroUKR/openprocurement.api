from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)


@resource(
    name="aboveThresholdUA:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="aboveThresholdUA",
    description="aboveThresholdUA tenders",
    accept="application/json",
)
class AboveThresholdUATenderResource(TendersResource):
    state_class = OpenUATenderDetailsState
