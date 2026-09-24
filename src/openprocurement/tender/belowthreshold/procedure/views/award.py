from logging import getLogger

from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.award import AwardState
from openprocurement.tender.core.procedure.views.award import TenderAwardResource

LOGGER = getLogger(__name__)


@resource(
    name="belowThreshold:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="belowThreshold",
)
class BelowThresholdTenderAwardResource(TenderAwardResource):
    state_class = AwardState
