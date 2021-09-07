from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from cornice.resource import resource


@resource(
    name="belowThreshold:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="belowThreshold",
    description="Tender chronograph",
)
class BelowThresholdChronographResource(TenderChronographResource):
    state_class = BelowThresholdTenderState

