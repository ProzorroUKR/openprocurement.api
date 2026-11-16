from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.competitivedialogue.procedure.state.stage2.criterion_rg_requirement_evidence import (
    CDStage2EUEligibleEvidenceState,
    CDStage2UAEligibleEvidenceState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)


class BaseStage2EligibleEvidenceResource(BaseEligibleEvidenceResource):
    pass


@resource(
    name="{}:Requirement Eligible Evidence".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2,
    description="Competitive Dialogue Stage 2 EU requirement evidence",
)
class Stage2EUEUEligibleEvidenceResource(BaseStage2EligibleEvidenceResource):
    state_class = CDStage2EUEligibleEvidenceState


@resource(
    name="{}:Requirement Eligible Evidence".format(ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2,
    description="Competitive Dialogue Stage 2 EU requirement evidence",
)
class Stage2UAEligibleEvidenceResource(BaseStage2EligibleEvidenceResource):
    state_class = CDStage2UAEligibleEvidenceState
