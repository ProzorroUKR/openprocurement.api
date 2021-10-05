from openprocurement.tender.core.procedure.views.chronograph import TenderChronographResource
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType="simple.defense",
    description="Tender chronograph",
)
class SimpleDefenseChronographResource(TenderChronographResource):
    state_class = OpenUADefenseTenderState
