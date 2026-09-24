from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.openuadefense.procedure.state.tender_details import (
    AboveThresholdUADefenseTenderDetailsState,
)


@resource(
    name="aboveThresholdUA.defense:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="aboveThresholdUA.defense tenders",
    accept="application/json",
)
class AboveThresholdUADefenseTenderResource(TendersResource):
    state_class = AboveThresholdUADefenseTenderDetailsState
