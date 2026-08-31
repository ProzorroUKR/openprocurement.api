from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource
from openprocurement.tender.limited.constants import NEGOTIATION, NEGOTIATION_QUICK, REPORTING
from openprocurement.tender.limited.procedure.models.criterion import LimitedCriterion, PatchLimitedCriterion
from openprocurement.tender.limited.procedure.state.criterion import LimitedCriterionState


@resource(
    name=f"{REPORTING}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{REPORTING}",
    description="Tender criteria",
)
class ReportingCriterionResource(BaseCriterionResource):
    state_class = LimitedCriterionState

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("tender")),
            validate_input_data(LimitedCriterion, allow_bulk=True),
        ),
        permission="create_criterion",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("tender")),
            validate_input_data(PatchLimitedCriterion),
            validate_patch_data_simple(LimitedCriterion, "criterion"),
        ),
        permission="edit_criterion",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()


@resource(
    name=f"{NEGOTIATION}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{NEGOTIATION}",
    description="Tender criteria",
)
class NegotiationCriterionResource(ReportingCriterionResource):
    pass


@resource(
    name=f"{NEGOTIATION_QUICK}:Tender Criteria",
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=f"{NEGOTIATION_QUICK}",
    description="Tender criteria",
)
class NegotiationQuickCriterionResource(ReportingCriterionResource):
    pass
