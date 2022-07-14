from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.question import UATenderQuestionResource


@resource(
    name="simple.defense:Tender Questions",
    collection_path="/tenders/{tender_id}/questions",
    path="/tenders/{tender_id}/questions/{question_id}",
    procurementMethodType="simple.defense",
    description="Tender questions",
)
class SimpleDefenseTenderQuestionResource(UATenderQuestionResource):
    pass
