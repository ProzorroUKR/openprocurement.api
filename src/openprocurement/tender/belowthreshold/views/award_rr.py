# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_rr import BaseAwardRequirementResponseResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="belowThreshold:Award Requirement Response",
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}",
    procurementMethodType="belowThreshold",
    description="Tender award requirement responses",
)
class AwardRequirementResponseResource(BaseAwardRequirementResponseResource):
    pass
