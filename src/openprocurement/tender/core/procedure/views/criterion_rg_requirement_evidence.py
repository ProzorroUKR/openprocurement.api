from logging import getLogger
from typing import Optional, List, Tuple

from pyramid.request import Request
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.criterion_rg_requirement_evidence import (
    EligibleEvidenceSerializer,
)
from openprocurement.tender.core.procedure.state.criterion_rq_requirement_evidence import EligibleEvidenceState
from openprocurement.tender.core.procedure.models.criterion import (
    EligibleEvidence,
    PatchEligibleEvidence
)
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import (
    resolve_criterion,
    resolve_requirement_group,
    resolve_requirement,
)
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
)


LOGGER = getLogger(__name__)


def resolve_eligible_evidence(request: Request) -> None:
    match_dict = request.matchdict
    if match_dict.get("evidence_id"):
        evidence_id = match_dict["evidence_id"]
        evidences = get_items(
            request,
            request.validated["requirement"],
            "eligibleEvidences",
            evidence_id,
        )
        request.validated["evidence"] = evidences[0]


class BaseEligibleEvidenceResource(TenderBaseResource):

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_evidence"),
            (Allow, "g:brokers", "edit_evidence"),
            (Allow, "g:Administrator", "edit_evidence"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]

    serializer_class = EligibleEvidenceSerializer
    state_class = EligibleEvidenceState

    def __init__(self, request: Request, context=None) -> None:
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_criterion(request)
            resolve_requirement_group(request)
            resolve_requirement(request)
            resolve_eligible_evidence(request)

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(EligibleEvidence),
        ),
        permission="create_evidence",
    )
    def collection_post(self) -> Optional[dict]:

        evidence = self.request.validated["data"]
        requirement = self.request.validated["requirement"]

        if "eligibleEvidences" not in requirement:
            requirement["eligibleEvidences"] = []
        requirement["eligibleEvidences"].append(evidence)

        self.state.evidence_on_post(requirement)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created requirement eligible evidence {evidence['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "requirement_eligible_evidence_create"},
                    {"evidence_id": evidence["id"]},
                ),
            )
            tender = self.request.validated["tender"]
            match_dict = self.request.matchdict
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                f"{tender['procurementMethodType']}:Requirement Eligible Evidence",
                tender_id=match_dict.get("tender_id"),
                criterion_id=match_dict.get("criterion_id"),
                requirement_group_id=match_dict.get("requirement_group_id"),
                requirement_id=match_dict.get("requirement_id"),
                evidence_id=evidence["id"],
            )
            return {"data": self.serializer_class(evidence).data}

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        requirement = self.request.validated["requirement"]
        data = tuple(self.serializer_class(req).data for req in requirement.get("eligibleEvidences", ""))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self) -> dict:
        data = self.serializer_class(self.request.validated["evidence"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(PatchEligibleEvidence),
                validate_patch_data_simple(EligibleEvidence, "evidence"),
        ),
        permission="edit_evidence",
    )
    def patch(self) -> Optional[dict]:
        updated_evidence = self.request.validated["data"]
        if not updated_evidence:
            return
        evidence = self.request.validated["evidence"]
        requirement = self.request.validated["requirement"]

        self.state.evidence_on_patch(evidence, updated_evidence)

        set_item(requirement, "eligibleEvidences", evidence["id"], updated_evidence)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Updated requirement eligible evidence {evidence['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_eligible_evidence_patch"}),
            )
            return {"data":  self.serializer_class(updated_evidence).data}

    @json_view(
        validators=(unless_administrator(validate_item_owner("tender"))),
        permission="edit_evidence",
    )
    def delete(self):
        evidence = self.request.validated["evidence"]
        requirement = self.request.validated["requirement"]

        self.state.evidence_on_delete(evidence)

        requirement["eligibleEvidences"].remove(evidence)
        if not requirement["eligibleEvidences"]:
            del requirement["eligibleEvidences"]

        if save_tender(self.request, modified=False):
            self.LOGGER.info(
                f"Deleted requirement eligible evidence {evidence['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_eligible_evidence_delete"}),
            )
            return {"data": self.serializer_class(evidence).data}
