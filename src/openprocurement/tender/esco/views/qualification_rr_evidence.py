# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_rr_evidence import (
    BaseQualificationRequirementResponseEvidenceResource,
)
from openprocurement.tender.openeu.utils import qualifications_resource


@qualifications_resource(
    name="esco:Qualification Requirement Response Evidence",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType="esco",
    description="ESCO qualification evidences",
)
class QualificationRequirementResponseEvidenceResource(
    BaseQualificationRequirementResponseEvidenceResource
):
    pass
