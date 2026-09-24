from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.award import (
    COAwardState,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=COMPETITIVE_ORDERING,
)
class COTenderAwardResource(TenderAwardResource):
    state_class = COAwardState
