# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_rr import BaseQualificationRequirementResponseResource
from openprocurement.tender.openeu.utils import qualifications_resource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE


@qualifications_resource(
    name="{}:Qualification Requirement Response".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU qualification requirement responses",
)
class CDEUStage2QualificationRequirementResponseResource(BaseQualificationRequirementResponseResource):
    pass
