from typing import Optional

from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.competitivedialogue.procedure.views.stage1.criterion_rg_requirement_evidence import (
    BaseCDEligibleEvidenceResource,
)
from openprocurement.tender.core.procedure.models.criterion import (
    EligibleEvidence,
    PatchEligibleEvidence
)
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement_evidence import (
    Stage1EligibleEvidenceState,
)
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    unless_admins,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple
)
from openprocurement.tender.competitivedialogue.procedure.validation import unless_cd_bridge
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


class BaseStage2EligibleEvidenceResource(BaseCDEligibleEvidenceResource):
    @json_view(
        content_type="application/json",
        validators=(
                unless_cd_bridge(unless_admins(unless_administrator(
                    validate_item_owner("tender")
                ))),
                validate_input_data(EligibleEvidence),
        ),
        permission="create_evidence",
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
                unless_cd_bridge(unless_admins(unless_administrator(
                    validate_item_owner("tender")
                ))),
                validate_input_data(PatchEligibleEvidence),
                validate_patch_data_simple(EligibleEvidence, "evidence"),
        ),
        permission="edit_evidence",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()


@resource(
    name="{}:Requirement Eligible Evidence".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU requirement evidence",
)
class Stage2EUEUEligibleEvidenceResource(BaseStage2EligibleEvidenceResource):
    state_class = Stage1EligibleEvidenceState


@resource(
    name="{}:Requirement Eligible Evidence".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 EU requirement evidence",
)
class Stage2UAEligibleEvidenceResource(BaseStage2EligibleEvidenceResource):
    state_class = Stage1EligibleEvidenceState
