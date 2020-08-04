# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    APIResource,
)
from openprocurement.tender.core.utils import save_tender, apply_patch
from openprocurement.tender.core.validation import (
    validate_eligible_evidence_data,
    validate_patch_eligible_evidence_data,
    validate_operation_ecriteria_objects,
)


class BaseTenderCriteriaRGRequirementEvidenceResource(APIResource):

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_eligible_evidence_data,
        ),
        permission="edit_tender"
    )
    def collection_post(self):

        evidence = self.request.validated["evidence"]
        tender = self.request.validated["tender"]
        self.request.context.eligibleEvidences.append(evidence)

        if (
            self.request.authenticated_role == "tender_owner"
            and tender.status == "active.tendering"
            and hasattr(tender, "invalidate_bids_data")
        ):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Created requirement eligible evidence {}".format(evidence.id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "requirement_eligible_evidence_create"},
                    {"evidence_id": evidence.id},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Requirement Eligible Evidence".format(self.request.validated["tender"].procurementMethodType),
                tender_id=self.request.validated["tender_id"],
                criterion_id=self.request.validated["criterion"].id,
                requirement_group_id=self.request.validated["requirement_group"].id,
                requirement_id=self.request.validated["requirement"].id,
                evidence_id=evidence.id,
            )
            return {"data": evidence.serialize("view")}

    @json_view(permission="view_tender")
    def collection_get(self):
        return {"data": [i.serialize("view") for i in self.request.context.eligibleEvidences]}

    @json_view(permission="view_tender")
    def get(self):
        return {"data": self.request.context.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
            validate_operation_ecriteria_objects,
            validate_patch_eligible_evidence_data,
        ),
        permission="edit_tender"
    )
    def patch(self):
        evidence = self.request.context
        apply_patch(self.request, save=False, src=evidence.serialize())
        tender = self.request.validated["tender"]
        if self.request.authenticated_role == "tender_owner" and hasattr(tender, "invalidate_bids_data"):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Updated requirement eligible evidence {}".format(evidence.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_eligible_evidence_patch"}),
            )
            return {"data": evidence.serialize("view")}

    @json_view(
        validators=(
            validate_operation_ecriteria_objects,
        ),
        permission="edit_tender"
    )
    def delete(self):
        evidence = self.request.context
        res = evidence.serialize("view")
        self.request.validated["requirement"].eligibleEvidences.remove(evidence)
        self.request.validated["tender"].modified = False
        tender = self.request.validated["tender"]

        if (
            self.request.authenticated_role == "tender_owner"
            and tender.status == "active.tendering"
            and hasattr(tender, "invalidate_bids_data")
        ):
            tender.invalidate_bids_data()

        if save_tender(self.request):
            self.LOGGER.info(
                "Deleted requirement eligible evidence {}".format(self.request.context.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "requirement_eligible_evidence_delete"}),
            )
            return {"data": res}
