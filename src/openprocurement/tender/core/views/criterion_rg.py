# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import (
    validate_requirement_group_data,
    validate_patch_requirement_group_data,
    validate_operation_ecriteria_objects,
    validate_patch_exclusion_ecriteria_objects,
)


class BaseTenderCriteriaRGResource(APIResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_exclusion_ecriteria_objects,
            validate_requirement_group_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):

        requirement_group = self.request.validated["requirementgroup"]
        self.request.context.requirementGroups.append(requirement_group)
        tender = self.request.validated["tender"]
        if (
            self.request.authenticated_role == "tender_owner"
            and tender.status == "active.tendering"
            and hasattr(tender, "invalidate_bids_data")
        ):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Created criteria requirement group {}".format(requirement_group.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "criteria_requirement_group_create"},
                    {"requirement_group_id": requirement_group.id},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Criteria Requirement Group".format(self.request.validated["tender"].procurementMethodType),
                tender_id=self.request.validated["tender_id"],
                criterion_id=self.request.validated["criterion"].id,
                requirement_group_id=requirement_group.id,
            )
            return {"data": requirement_group.serialize("view")}

    @json_view(permission="view_tender")
    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.context.requirementGroups]}

    @json_view(permission="view_tender")
    def get(self):
        return {"data": self.request.validated["requirement_group"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_exclusion_ecriteria_objects,
            validate_patch_requirement_group_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        requirement_group = self.request.context
        apply_patch(self.request, save=False, src=requirement_group.serialize())
        tender = self.request.validated["tender"]
        if self.request.authenticated_role == "tender_owner" and hasattr(tender, "invalidate_bids_data"):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated criteria requirement group {}".format(requirement_group.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "criteria_requirement_group_patch"}),
            )
            return {"data": requirement_group.serialize("view")}
