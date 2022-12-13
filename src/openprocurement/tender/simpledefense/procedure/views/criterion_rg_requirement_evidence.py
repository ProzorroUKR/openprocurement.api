from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.criterion_rg_requirement_evidence import (
    EligibleEvidenceResource as OpenUAEligibleEvidenceResource,
)


@resource(
    name="simple.defense:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}"
                    "/requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
         "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense requirement evidence",
)
class EligibleEvidenceResource(OpenUAEligibleEvidenceResource):
    pass
