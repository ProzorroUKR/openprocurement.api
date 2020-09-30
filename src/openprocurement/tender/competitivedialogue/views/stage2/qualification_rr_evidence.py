# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_rr_evidence import (
    BaseQualificationRequirementResponseEvidenceResource,
)
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@qualifications_resource(
    name="{}:Qualification Requirement Response Evidence".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Tender EU qualification evidences",
)
class CDEUStage2QualificationRequirementResponseEvidenceResource(
    BaseQualificationRequirementResponseEvidenceResource
):
    pass
