from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.criterion import CriterionResource as OpenUACriterionResource


@resource(
    name="simple.defense:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense criteria",
)
class CriterionResource(OpenUACriterionResource):
    pass
