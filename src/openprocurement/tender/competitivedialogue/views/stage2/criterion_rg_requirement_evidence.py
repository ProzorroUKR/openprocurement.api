# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement_evidence import (
    BaseTenderCriteriaRGRequirementEvidenceResource,
)
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@optendersresource(
    name="{}:Requirement Eligible Evidence".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU requirement evidence",
)
class CDEUCriteriaRGRequirementEvidenceResource(BaseTenderCriteriaRGRequirementEvidenceResource):
    pass


@optendersresource(
    name="{}:Requirement Eligible Evidence".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA requirement evidence",
)
class CDUACriteriaRGRequirementEvidenceResource(BaseTenderCriteriaRGRequirementEvidenceResource):
    pass
