# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_rr_evidence import (
    BaseQualificationRequirementResponseEvidenceResource,
)
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.competitivedialogue.constants import CD_EU_TYPE, CD_UA_TYPE


@qualifications_resource(
    name="{}:Qualification Requirement Response Evidence".format(CD_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_EU_TYPE,
    description="Competitive Dialogue EU qualification evidences",
)
class CDEUQualificationRequirementResponseEvidenceResource(
    BaseQualificationRequirementResponseEvidenceResource
):
    pass


@qualifications_resource(
    name="{}:Qualification Requirement Response Evidence".format(CD_UA_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}"
                    "/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/"
         "requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=CD_UA_TYPE,
    description="Competitive Dialogue UA qualification evidences",
)
class CDUAQualificationRequirementResponseEvidenceResource(
    BaseQualificationRequirementResponseEvidenceResource
):
    pass
