from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
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
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseCriterionResource(BaseCriterionResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdCriterionState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUACriterionState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUCriterionState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUACriterionState, OpenTenderingEUCriterionState
        ),
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseCriterionState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COStateClass(COShortCriterionState, COLongCriterionState),
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdCriterionState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPCriterionState,
    }
