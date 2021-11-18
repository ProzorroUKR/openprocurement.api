from openprocurement.tender.openuadefense.procedure.views.award import UADefenseTenderAwardResource
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="simple.defense",
)
class SimpleDefenseTenderAwardResource(UADefenseTenderAwardResource):
    pass
