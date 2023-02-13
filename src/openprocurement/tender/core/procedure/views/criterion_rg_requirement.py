from logging import getLogger
from typing import Optional, List, Tuple
from copy import copy

from pyramid.request import Request
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.tender.core.constants import CRITERION_LIFE_CYCLE_COST_IDS
from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import context_unpack, json_view,  get_now
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.criterion_rg_requirement import (
    RequirementSerializer,
    PutCancelledRequirementSerializer,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementState
from openprocurement.tender.core.procedure.models.criterion import (
    PostRequirement,
    PatchRequirement,
    PatchExclusionLccRequirement,
    PutRequirement,
    PutExclusionLccRequirement,
    Requirement,
)
from openprocurement.tender.core.procedure.views.criterion_rg import resolve_criterion, resolve_requirement_group
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
)


LOGGER = getLogger(__name__)


def resolve_requirement(request: Request) -> None:
    match_dict = request.matchdict
    if match_dict.get("requirement_id"):
        requirement_id = match_dict["requirement_id"]
        requirements = get_items(
            request,
            request.validated["requirement_group"],
            "requirements",
            requirement_id,
        )
        request.validated["requirement"] = requirements[-1]


def validate_resolve_requirement_input_data(
        default_model: object,
        exclusion_model: object,
        none_means_remove: bool = False
) -> callable:
    def validate(request, **kwargs):
        criterion = request.validated["criterion"]
        classification_id = criterion["classification"]["id"]
        input_model = default_model
        if classification_id.startswith("CRITERION.EXCLUSION") or classification_id in CRITERION_LIFE_CYCLE_COST_IDS:
            input_model = exclusion_model
        return validate_input_data(input_model, none_means_remove=none_means_remove)(request, **kwargs)
    return validate


class BaseRequirementResource(TenderBaseResource):

    def __acl__(self) -> List[Tuple[str, str, str]]:
        return [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_requirement"),
            (Allow, "g:brokers", "edit_requirement"),
            (Allow, "g:Administrator", "edit_requirement"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]

    serializer_class = RequirementSerializer
    state_class = RequirementState

    def __init__(self, request: Request, context=None) -> None:
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_criterion(request)
            resolve_requirement_group(request)
            resolve_requirement(request)

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_input_data(PostRequirement),
        ),
        permission="create_requirement",
    )
    def collection_post(self) -> Optional[dict]:

        requirement = self.request.validated["data"]
        requirement_group = self.request.validated["requirement_group"]

        if "requirements" not in requirement_group:
            requirement_group["requirements"] = []
        requirement_group["requirements"].append(requirement)

        self.state.requirement_on_post(requirement)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created requirement group requirement {requirement['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "requirement_group_requirement_create"},
                    {"requirement_id": requirement["id"]},
                ),
            )
            self.request.response.status = 201
            tender = self.request.validated['tender']
            match_dict = self.request.matchdict
            self.request.response.headers["Location"] = self.request.route_url(
                f"{tender['procurementMethodType']}:Requirement Group Requirement",
                tender_id=match_dict.get("tender_id"),
                criterion_id=match_dict.get("criterion_id"),
                requirement_group_id=match_dict.get("requirement_group_id"),
                requirement_id=requirement["id"],
            )
            return {"data": self.serializer_class(requirement).data}

    @json_view(permission="view_tender")
    def collection_get(self) -> dict:
        requirement_group = self.request.validated["requirement_group"]
        data = tuple(self.serializer_class(req).data for req in requirement_group.get("requirements", ""))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self) -> dict:
        data = self.serializer_class(self.request.validated["requirement"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_resolve_requirement_input_data(PatchRequirement, PatchExclusionLccRequirement),
                validate_patch_data_simple(Requirement, "requirement"),
        ),
        permission="edit_requirement",
    )
    def patch(self) -> Optional[dict]:
        updated_requirement = self.request.validated["data"]
        if not updated_requirement:
            return
        requirement = self.request.validated["requirement"]
        requirement_group = self.request.validated["requirement_group"]

        self.state.requirement_on_patch(requirement, updated_requirement)

        set_item(requirement_group, "requirements", requirement["id"], updated_requirement)

        if save_tender(self.request):
            self.LOGGER.info(
                f"Updated requirement group requirement {requirement_group['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_group_requirement_patch"}),
            )
            return {"data":  self.serializer_class(updated_requirement).data}

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(validate_item_owner("tender")),
                validate_resolve_requirement_input_data(
                    PutRequirement,
                    PutExclusionLccRequirement,
                    none_means_remove=True
                ),
                validate_patch_data_simple(Requirement, "requirement"),
        ),
        permission="edit_requirement",
    )
    def put(self):
        requirement = self.request.validated["requirement"]
        updated_requirement = self.request.validated["data"]

        self.state.requirement_on_put(requirement, updated_requirement)

        if (
            not updated_requirement
            or requirement == updated_requirement
            or (requirement["status"] == "cancelled" and updated_requirement["status"] != "active")
        ):
            return {"data": (self.serializer_class(requirement).data, )}

        now = get_now().isoformat()
        if updated_requirement.get("status") != "cancelled":

            updated_requirement["datePublished"] = now
            if "dateModified" in updated_requirement:
                del updated_requirement["dateModified"]
            self.request.validated["requirement_group"]["requirements"].append(updated_requirement)
        else:
            updated_requirement = requirement

        if requirement["status"] == "active":
            requirement["status"] = "cancelled"
            requirement["dateModified"] = now

        if save_tender(self.request):
            self.LOGGER.info(
                f"New version of requirement {requirement['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_group_requirement_put"}),
            )
            return {"data": (
                self.serializer_class(updated_requirement).data,
                PutCancelledRequirementSerializer(requirement).data,
            )}
