from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState
from cornice.resource import resource


@resource(
    name="aboveThresholdUA.defense:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender chronograph",
)
class DefenseChronographResource(TenderChronographResource):
    state_class = OpenUADefenseTenderState
