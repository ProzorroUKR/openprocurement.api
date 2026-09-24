from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.criterion_rg_requirement_evidence import (
    CDStage2EligibleEvidenceState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)


class BaseStage2EligibleEvidenceResource(BaseEligibleEvidenceResource):
    pass


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
    state_class = CDStage2EligibleEvidenceState


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
    state_class = CDStage2EligibleEvidenceState
