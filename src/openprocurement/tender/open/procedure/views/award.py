from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.award import (
    AboveThresholdAwardState,
    AboveThresholdUAAwardState,
    BelowThresholdAwardState,
    COAwardState,
    DefenseAwardState,
    RFPAwardState,
    SimpleDefenseAwardState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenTenderAwardResource(TenderAwardResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdAwardState,
        ABOVE_THRESHOLD_UA: AboveThresholdUAAwardState,
        ABOVE_THRESHOLD_EU: AboveThresholdUAAwardState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseAwardState,
        SIMPLE_DEFENSE: SimpleDefenseAwardState,
        COMPETITIVE_ORDERING: COAwardState,
        BELOW_THRESHOLD: BelowThresholdAwardState,
        REQUEST_FOR_PROPOSAL: RFPAwardState,
    }
