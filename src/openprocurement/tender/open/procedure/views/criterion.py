from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    OPEN_TENDERING,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.criterion import (
    AboveThresholdCriterionState,
    AboveThresholdEUCriterionState,
    AboveThresholdUACriterionState,
    BelowThresholdCriterionState,
    COLongCriterionState,
    COShortCriterionState,
    OpenTenderingEUCriterionState,
    OpenTenderingUACriterionState,
    RFPCriterionState,
    SimpleDefenseCriterionState,
)
from openprocurement.tender.open.procedure.views.base import (
    COStateClass,
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    description="Tender criteria",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        OPEN_TENDERING,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseCriterionResource(BaseCriterionResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdCriterionState,
        ABOVE_THRESHOLD_UA: AboveThresholdUACriterionState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUCriterionState,
        OPEN_TENDERING: OpenTenderingStateClass(OpenTenderingUACriterionState, OpenTenderingEUCriterionState),
        SIMPLE_DEFENSE: SimpleDefenseCriterionState,
        COMPETITIVE_ORDERING: COStateClass(COShortCriterionState, COLongCriterionState),
        BELOW_THRESHOLD: BelowThresholdCriterionState,
        REQUEST_FOR_PROPOSAL: RFPCriterionState,
    }
