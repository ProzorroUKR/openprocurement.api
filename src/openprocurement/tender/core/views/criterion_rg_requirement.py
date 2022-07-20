# -*- coding: utf-8 -*-
from copy import copy

from openprocurement.api.utils import (
    json_view,
    context_unpack,
    get_now,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import (
    validate_requirement_data,
    validate_patch_requirement_data,
    validate_operation_ecriteria_objects,
    validate_patch_exclusion_ecriteria_objects,
    validate_change_requirement_objects,
    validate_put_requirement_objects,
)


class BaseTenderCriteriaRGRequirementResource(BaseResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_exclusion_ecriteria_objects,
            validate_requirement_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):

        requirement = self.request.validated["requirement"]
        self.request.context.requirements.append(requirement)
        tender = self.request.validated["tender"]
        if (
            self.request.authenticated_role == "tender_owner"
            and tender.status == "active.tendering"
            and hasattr(tender, "invalidate_bids_data")
        ):
            tender.invalidate_bids_data()

        if save_tender(self.request, validate=True):
            self.LOGGER.info(
                "Created requirement group requirement {}".format(requirement.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "requirement_group_requirement_create"},
                    {"requirement_id": requirement.id},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Requirement Group Requirement".format(self.request.validated["tender"].procurementMethodType),
                tender_id=self.request.validated["tender_id"],
                criterion_id=self.request.validated["criterion"].id,
                requirement_group_id=self.request.validated["requirement_group"].id,
                requirement_id=requirement.id
            )
            return {"data": requirement.serialize("view")}

    @json_view(permission="view_tender")
    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.context.requirements]}

    @json_view(permission="view_tender")
    def get(self):
        return {"data": self.request.validated["requirement"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_change_requirement_objects,
            validate_patch_requirement_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        requirement = self.request.context
        apply_patch(self.request, save=False, src=requirement.serialize())
        tender = self.request.validated["tender"]

        if self.request.authenticated_role == "tender_owner" and hasattr(tender, "invalidate_bids_data"):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated  {}".format(requirement.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_group_requirement_patch"}),
            )
            return {"data": requirement.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_put_requirement_objects,
            validate_patch_requirement_data,
        ),
        permission="edit_tender"
    )
    def put(self):
        old_requirement = self.request.context
        requirement = old_requirement
        if self.request.validated["data"].get("status") != "cancelled":
            model = type(old_requirement)
            data = copy(self.request.validated["data"])
            for attr_name in type(old_requirement)._fields:
                if data.get(attr_name) is None:
                    data[attr_name] = getattr(old_requirement, attr_name)
            # To avoid new version creation if no changes and only id's were regenerated
            if "eligibleEvidences" not in self.request.json.get("data", {}):
                data["eligibleEvidences"] = [
                    evidence.to_primitive(role="create") for evidence in getattr(old_requirement, "eligibleEvidences")
                ]

            requirement = model(data)
            if old_requirement.to_primitive() == requirement.to_primitive():
                return {"data": (old_requirement.serialize("view"),)}

            requirement.datePublished = get_now()
            requirement.dateModified = None
            self.request.validated["requirement_group"].requirements.append(requirement)

        if old_requirement.status == "active":
            old_requirement.status = "cancelled"
            old_requirement.dateModified = get_now()

        tender = self.request.validated["tender"]
        if (
                self.request.authenticated_role == "tender_owner"
                and tender.status == "active.tendering"
                and hasattr(tender, "invalidate_bids_data")
        ):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "New version of requirement {}".format(requirement.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_group_requirement_put"}),
            )
            return {"data": (requirement.serialize("view"), old_requirement.serialize("view_old"))}
