from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name="belowThreshold:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="belowThreshold",
    description="Tender chronograph",
)
class BelowThresholdChronographResource(TenderChronographResource):
    state_class = BelowThresholdTenderState
