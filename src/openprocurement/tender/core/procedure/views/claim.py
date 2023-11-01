from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from openprocurement.api.utils import json_view, update_logging_context, LOGGER
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin, TenderClaimState
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.models.claim import (
    PostClaim,
    ClaimOwnerPatchClaim,
    TenderOwnerPatchClaim,
    Claim,
)
from openprocurement.tender.core.procedure.serializers.complaint import TenderComplaintSerializer, ComplaintSerializer
from openprocurement.tender.core.procedure.utils import set_ownership
from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    set_item,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_any,
    validate_item_owner,
    validate_input_data,
    validate_patch_data,
    validate_input_data_from_resolved_model,
    validate_data_documents,
)
from openprocurement.api.utils import context_unpack


def resolve_claim(request, context="tender"):
    match_dict = request.matchdict
    if claim_id := match_dict.get("complaint_id"):
        claims = get_items(request, request.validated[context], "complaints", claim_id)
        request.validated["claim"] = claims[0]


def calculate_total_complaints(tender):
    total_complaints = len(tender.get("complaints", ""))
    for k in ("cancellations", "awards", "qualifications"):
        if k in tender:
            total_complaints += sum(len(i.get("complaints", "")) for i in tender[k])
    return total_complaints


class BaseClaimResource(TenderBaseResource):
    item_name = "tender"   # tender or award
    serializer_class = ComplaintSerializer

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_claim"),
            (Allow, "g:brokers", "edit_claim"),
            (Allow, "g:Administrator", "edit_claim"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    @json_view(
        content_type="application/json",
        permission="create_claim",
        validators=(
            validate_input_data(PostClaim),
            validate_data_documents(route_key="claim_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"bid_id": "__new__"})

        context = self.request.validated[self.item_name]
        tender = self.request.validated["tender"]
        claim = self.request.validated["data"]
        access = set_ownership(claim, self.request)

        claim_number = calculate_total_complaints(tender) + 1
        claim["complaintID"] = f"{tender['tenderID']}.{self.request.registry.server_id}{claim_number}"

        self.state.validate_claim_on_post(claim)
        if "complaints" not in context:
            context["complaints"] = []
        context["complaints"].append(claim)
        self.state.claim_on_post(claim)

        if save_tender(self.request):
            LOGGER.info(
                f"Created {self.context} claim {claim['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.context}_claim_create"},
                                     {"claim_id": claim["id"]}),
            )
            self.request.response.status = 201
            route_params = dict(
                tender_id=tender["_id"],
                complaint_id=claim["id"],
            )
            if self.item_name != "tender":
                route_params[f"{self.item_name}_id"] = context["id"]
                route_name = f"{tender['procurementMethodType']}:Tender {self.item_name.capitalize()} Complaints Get"
            else:
                route_name = f"{tender['procurementMethodType']}:Tender Complaints Get"
            self.request.response.headers["Location"] = self.request.route_url(route_name, **route_params)
            return {"data": self.serializer_class(claim).data, "access": access}

    @json_view(
        content_type="application/json",
        validators=(
            unless_admins(
                validate_any(
                    validate_item_owner("claim"),
                    validate_item_owner("tender"),
                )
            ),
            validate_input_data_from_resolved_model(),
            validate_patch_data(Claim, item_name="claim"),
        ),
        permission="edit_claim",
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            claim = self.request.validated["claim"]
            self.state.validate_claim_on_patch(claim, updated)

            context = self.request.validated[self.item_name]
            set_item(context, "complaints", claim["id"], updated)
            self.state.claim_on_patch(claim, updated)

            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated {self.context} claim {claim['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.context}_claim_patch"}),
                )
                return {"data": self.serializer_class(updated).data}


class TenderClaimResource(BaseClaimResource):
    state_class = TenderClaimState

    @property
    def serializer_class(self):
        if self.request.method == "POST":
            return ComplaintSerializer
        else:
            return TenderComplaintSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_claim(request)
