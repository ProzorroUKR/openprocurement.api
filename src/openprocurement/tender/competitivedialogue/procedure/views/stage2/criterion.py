from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.criterion import (
    CDCriterionState,
)
from openprocurement.tender.core.procedure.models.criterion import (
    Criterion,
    PatchCriterion,
)
from openprocurement.tender.core.procedure.views.criterion import BaseCriterionResource


class BaseStage2CriterionResource(BaseCriterionResource):
    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("tender"))),
            validate_input_data(Criterion, allow_bulk=True),
        ),
        permission="create_criterion",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(unless_administrator(validate_item_owner("tender"))),
            validate_input_data(PatchCriterion),
            validate_patch_data_simple(Criterion, "criterion"),
        ),
        permission="edit_criterion",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()


@resource(
    name="{}:Tender Criteria".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU criteria",
)
class Stage2EUCriterionResource(BaseStage2CriterionResource):
    state_class = CDCriterionState


@resource(
    name="{}:Tender Criteria".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria",
    path="/tenders/{tender_id}/criteria/{criterion_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA criteria",
)
class Stage2UACriterionResource(BaseStage2CriterionResource):
    state_class = CDCriterionState
