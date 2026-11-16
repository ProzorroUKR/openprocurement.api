from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg_requirement_evidence import (
    BaseEligibleEvidenceResource,
)
from openprocurement.tender.pricequotation.procedure.state.criterion_rg_requirement_evidence import (
    PQEligibleEvidenceState,
)


@resource(
    name=f"{ProcurementMethodType.PRICE_QUOTATION}:Requirement Eligible Evidence",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}"
    "/requirements/{requirement_id}/evidences",
    path="/tenders/{tender_id}/criteria/{criterion_id}/"
    "requirement_groups/{requirement_group_id}/requirements/{requirement_id}/evidences/{evidence_id}",
    procurementMethodType=ProcurementMethodType.PRICE_QUOTATION,
    description=f"{ProcurementMethodType.PRICE_QUOTATION} Tender requirement evidence",
)
class EligibleEvidenceResource(BaseEligibleEvidenceResource):
    state_class = PQEligibleEvidenceState
