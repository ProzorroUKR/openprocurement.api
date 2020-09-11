# -*- coding: utf-8 -*-
from openprocurement.tender.core.views.award_rr_evidence import BaseAwardRequirementResponseEvidenceResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.competitivedialogue.constants import STAGE_2_EU_TYPE, STAGE_2_UA_TYPE


@optendersresource(
    name="{}:Award Requirement Response Evidence".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_EU_TYPE,
    description="Competitive Dialogue Stage 2 EU award evidences",
)
class CDEUAwardRequirementResponseEvidenceResource(
    BaseAwardRequirementResponseEvidenceResource
):
    pass


@optendersresource(
    name="{}:Award Requirement Response Evidence".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences",
    path="/tenders/{tender_id}/awards/{award_id}/requirement_responses/{requirement_response_id}/evidences/{evidence_id}",
    procurementMethodType=STAGE_2_UA_TYPE,
    description="Competitive Dialogue Stage 2 UA award evidences",
)
class CDUAAwardRequirementResponseEvidenceResource(
    BaseAwardRequirementResponseEvidenceResource
):
    pass