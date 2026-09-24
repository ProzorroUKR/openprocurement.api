from cornice.resource import resource

from openprocurement.tender.openuadefense.procedure.views.tender import (
    AboveThresholdUADefenseTenderResource,
)
from openprocurement.tender.simpledefense.procedure.state.tender_details import (
    SimpleDefenseTenderDetailsState,
)


@resource(
    name="simple.defense:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="simple.defense",
    description="aboveThresholdUA.defense tenders",
    accept="application/json",
)
class SimpleDefenseTenderResource(AboveThresholdUADefenseTenderResource):
    state_class = SimpleDefenseTenderDetailsState
