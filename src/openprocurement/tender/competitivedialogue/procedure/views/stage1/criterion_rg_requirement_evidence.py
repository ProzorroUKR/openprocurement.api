from typing import List, Tuple, Optional

from cornice.resource import resource
from pyramid.security import Allow

from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import BaseEligibleEvidenceResource
from openprocurement.tender.competitivedialogue.procedure.state.criterion_rg_requirement_evidence import (
    Stage1EligibleEvidenceState,
)
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


class BaseCDEligibleEvidenceResource(BaseEligibleEvidenceResource):
    def __acl__(self) -> List[Tuple[str, str, str]]:
        acl = super().__acl__()
        acl.extend([
            (Allow, "g:competitive_dialogue", "create_requirement"),
            (Allow, "g:competitive_dialogue", "edit_requirement"),
        ])
        return acl


@resource(
    name="{}:Requirement Eligible Evidence".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU requirement evidence",
)
class CDEUEligibleEvidenceResource(BaseCDEligibleEvidenceResource):
    state_class = Stage1EligibleEvidenceState


@resource(
    name="{}:Requirement Eligible Evidence".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA requirement evidence",
)
class CDUAEligibleEvidenceResource(BaseCDEligibleEvidenceResource):
    state_class = Stage1EligibleEvidenceState
