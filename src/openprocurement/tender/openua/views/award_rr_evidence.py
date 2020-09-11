# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_rr_evidence import BaseAwardRequirementResponseEvidenceResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="aboveThresholdUA:Award Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender UA award evidences",
)
class AwardRequirementResponseEvidenceResource(
    BaseAwardRequirementResponseEvidenceResource
):
    pass
