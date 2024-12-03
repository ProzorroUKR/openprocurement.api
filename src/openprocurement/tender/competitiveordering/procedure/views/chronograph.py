from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender chronograph",
)
class OpenUAChronographResource(TenderChronographResource):
    state_class = OpenTenderState
