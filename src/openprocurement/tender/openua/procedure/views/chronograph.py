from cornice.resource import resource

from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


@resource(
    name="aboveThresholdUA:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA chronograph",
)
class OpenUAChronographResource(TenderChronographResource):
    state_class = OpenUATenderState
