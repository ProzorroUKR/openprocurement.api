# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.belowthreshold.views.criterion_rg_requirement_evidence import (
    TenderCriteriaRGRequirementEvidenceResource,
)


@optendersresource(
    name="closeFrameworkAgreementSelectionUA:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/"
                    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender requirement evidence",
)
class TenderCriteriaRGRequirementEvidenceResource(TenderCriteriaRGRequirementEvidenceResource):
    pass
