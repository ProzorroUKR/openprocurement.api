# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.views.criterion_rg_requirement_evidence import (
    BaseTenderCriteriaRGRequirementEvidenceResource,
)


@optendersresource(
    name="aboveThresholdEU:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender requirement evidence",
)
class TenderUaCriteriaRGRequirementEvidenceResource(BaseTenderCriteriaRGRequirementEvidenceResource):
    pass
