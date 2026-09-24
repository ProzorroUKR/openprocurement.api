from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.openuadefense.procedure.state.award import AwardState


@resource(
    name="aboveThresholdUA.defense:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="aboveThresholdUA.defense",
)
class UADefenseTenderAwardResource(TenderAwardResource):
    state_class = AwardState
