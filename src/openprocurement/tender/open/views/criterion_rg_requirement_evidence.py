# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement_evidence import (
    BaseTenderCriteriaRGRequirementEvidenceResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


# @optendersresource(
#     name=f"{ABOVE_THRESHOLD}:Requirement Eligible Evidence",
#     collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
#     path="/tenders/{tender_id}/criteria/{criterion_id}/"
#          "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
#     procurementMethodType=ABOVE_THRESHOLD,
#     description="Tender requirement evidence",
# )
# class TenderUaCriteriaRGRequirementEvidenceResource(BaseTenderCriteriaRGRequirementEvidenceResource):
#     pass
