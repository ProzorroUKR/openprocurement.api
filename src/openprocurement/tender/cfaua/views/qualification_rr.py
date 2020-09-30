# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.qualification_rr import BaseQualificationRequirementResponseResource
from openprocurement.tender.cfaua.utils import qualifications_resource


@qualifications_resource(
    name="closeFrameworkAgreementUA:Qualification Requirement Response",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification requirement responses",
)
class QualificationRequirementResponseResource(BaseQualificationRequirementResponseResource):
    pass
