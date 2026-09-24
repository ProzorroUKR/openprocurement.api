from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.award import AwardState


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=ABOVE_THRESHOLD,
)
class UATenderAwardResource(TenderAwardResource):
    state_class = AwardState
