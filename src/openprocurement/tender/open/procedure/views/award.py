from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX, OpenProcurementMethodType
from openprocurement.tender.open.procedure.state.award import (
    AboveThresholdAwardState,
    AboveThresholdUAAwardState,
    BelowThresholdAwardState,
    COAwardState,
    DefenseAwardState,
    OpenTenderingAwardState,
    RFPAwardState,
    SimpleDefenseAwardState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=OpenProcurementMethodType,
)
class OpenTenderAwardResource(TenderAwardResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdAwardState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUAAwardState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdUAAwardState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingAwardState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseAwardState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseAwardState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COAwardState,
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdAwardState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPAwardState,
    }
