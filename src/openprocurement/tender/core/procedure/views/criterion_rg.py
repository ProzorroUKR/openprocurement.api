from logging import getLogger
from typing import Optional, List, Tuple

from pyramid.request import Request
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.criterion_rg import RequirementGroupSerializer
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupState
from openprocurement.tender.core.procedure.models.criterion import (
    RequirementGroup,
    PatchRequirementGroup,
)
from openprocurement.tender.core.procedure.views.criterion import resolve_criterion
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
)


LOGGER = getLogger(__name__)


def resolve_requirement_group(request: Request) -> None:
    match_dict = request.matchdict
    if match_dict.get("requirement_group_id"):
        requirement_group_id = match_dict["requirement_group_id"]
        requirement_groups = get_items(
            request,
            request.validated["criterion"],
            "requirementGroups",
            requirement_group_id,
        )
        request.validated["requirement_group"] = requirement_groups[0]


class BaseRequirementGroupResource(TenderBaseResource):

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_rg"),
            (Allow, "g:brokers", "edit_rg"),
            (Allow, "g:Administrator", "edit_rg"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]

    serializer_class = RequirementGroupSerializer
    state_class = RequirementGroupState

    def __init__(self, request: Request, context=None) -> None:
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_criterion(request)
            resolve_requirement_group(request)

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(RequirementGroup),
        ),
        permission="create_rg",
    )
    def collection_post(self) -> Optional[dict]:
        requirement_group = self.request.validated["data"]
        criterion = self.request.validated["criterion"]

        if "requirementGroups" not in criterion:
            criterion["requirementGroups"] = []
        criterion["requirementGroups"].append(requirement_group)

        self.state.requirement_group_on_post(requirement_group)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created criteria requirement group {requirement_group['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "criteria_requirement_group_create"},
                    {"requirement_group_id": requirement_group["id"]},
                ),
            )
            self.request.response.status = 201
            return {"data": self.serializer_class(requirement_group).data}

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        criterion = self.request.validated["criterion"]
        data = tuple(self.serializer_class(rg).data for rg in criterion.get("requirementGroups", ""))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self) -> dict:
        data = self.serializer_class(self.request.validated["requirement_group"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(PatchRequirementGroup),
                validate_patch_data_simple(RequirementGroup, "requirement_group"),
        ),
        permission="edit_rg",
    )
    def patch(self) -> Optional[dict]:
        updated_requirement_group = self.request.validated["data"]
        if not updated_requirement_group:
            return
        requirement_group = self.request.validated["requirement_group"]
        criterion = self.request.validated["criterion"]
        self.state.requirement_group_on_patch(requirement_group, updated_requirement_group)
        set_item(criterion, "requirementGroups", requirement_group["id"], updated_requirement_group)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Updated criteria requirement group {requirement_group['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "criteria_requirement_group_patch"}),
            )
            return {"data":  self.serializer_class(updated_requirement_group).data}
