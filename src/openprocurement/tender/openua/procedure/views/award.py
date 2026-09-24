from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.openua.procedure.state.award import AwardState


@resource(
    name="aboveThresholdUA:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="aboveThresholdUA",
)
class UATenderAwardResource(TenderAwardResource):
    state_class = AwardState
