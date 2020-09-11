# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import (
    validate_criterion_data,
    validate_patch_criterion_data,
    validate_operation_ecriteria_objects,
    validate_patch_exclusion_ecriteria_objects,
)


class BaseTenderCriteriaResource(APIResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_criterion_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):

        criterions = self.request.validated["criterions"]
        self.request.context.criteria.extend(criterions)
        tender = self.request.validated["tender"]

        if (
            self.request.authenticated_role == "tender_owner"
            and tender.status == "active.tendering"
            and hasattr(tender, "invalidate_bids_data")
        ):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            for criterion in criterions:
                self.LOGGER.info(
                    "Created tender criterion {}".format(criterion.id),
                    extra=context_unpack(
                        self.request, {"MESSAGE_ID": "tender_criterion_create"}, {"criterion_id": criterion.id}
                    ),
                )

            self.request.response.status = 201

            return {"data": [i.serialize("view") for i in criterions]}

    @json_view(permission="view_tender")
    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.context.criteria]}

    @json_view(permission="view_tender")
    def get(self):
        return {"data": self.request.validated["criterion"].serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_exclusion_ecriteria_objects,
            validate_patch_criterion_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        criterion = self.request.context
        tender = self.request.validated["tender"]
        apply_patch(self.request, save=False, src=criterion.serialize())

        if self.request.authenticated_role == "tender_owner" and hasattr(tender, "invalidate_bids_data"):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated tender criterion {}".format(criterion.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "tender_criterion_patch"}),
            )
            return {"data": criterion.serialize("view")}
