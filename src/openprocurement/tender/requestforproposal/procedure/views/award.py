from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.requestforproposal.procedure.state.award import AwardState

LOGGER = getLogger(__name__)


@resource(
    name="requestForProposal:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="requestForProposal",
)
class RequestForProposalTenderAwardResource(TenderAwardResource):
    state_class = AwardState
