from cornice.resource import resource

from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.simpledefense.procedure.state.tender import (
    SimpleDefenseTenderState,
)


@resource(
    name="simple.defense:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="simple.defense",
    description="Tender chronograph",
)
class SimpleDefenseChronographResource(TenderChronographResource):
    state_class = SimpleDefenseTenderState
