from cornice.resource import resource

from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_GROUP,
    ABOVE_THRESHOLD_GROUP_NAME,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender chronograph",
)
class OpenUAChronographResource(TenderChronographResource):
    state_class = OpenTenderState
