from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement_evidence import (
    CDEligibleEvidenceState,
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)


@resource(
    name="{}:Requirement Eligible Evidence".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU requirement evidence",
)
class CDEUEligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = CDEligibleEvidenceState


@resource(
    name="{}:Requirement Eligible Evidence".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA requirement evidence",
)
class CDUAEligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = CDEligibleEvidenceState
