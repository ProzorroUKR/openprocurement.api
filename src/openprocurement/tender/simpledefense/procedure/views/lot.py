from cornice.resource import resource

from openprocurement.tender.openuadefense.procedure.views.lot import OpenUADefenseLotResource


@resource(
    name="simple.defense:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="simple.defense",
    description="Simple defense lots",
)
class SimpleDefenseLotResource(OpenUADefenseLotResource):
    pass
