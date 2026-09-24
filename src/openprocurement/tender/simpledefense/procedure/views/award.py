from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.simpledefense.procedure.state.award import (
    SimpleDefenseAwardState,
)


@resource(
    name="simple.defense:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="simple.defense",
)
class SimpleDefenseTenderAwardResource(TenderAwardResource):
    state_class = SimpleDefenseAwardState
