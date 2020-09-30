# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_rr import BaseQualificationRequirementResponseResource
from openprocurement.tender.openeu.utils import qualifications_resource


@qualifications_resource(
    name="esco:Qualification Requirement Response",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="esco",
    description="Tender EU qualification requirement responses",
)
class QualificationRequirementResponseResource(BaseQualificationRequirementResponseResource):
    pass
