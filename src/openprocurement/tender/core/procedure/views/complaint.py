from openprocurement.api.utils import json_view, update_logging_context, LOGGER
from openprocurement.tender.core.procedure.state.complaint import ComplaintState
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.views.claim import calculate_total_complaints
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer, TenderComplaintSerializer
from openprocurement.tender.core.procedure.models.complaint import PostComplaint, Complaint
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from openprocurement.tender.core.procedure.utils import (
    save_tender,
    get_items,
    set_item,
    set_ownership,
)
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    unless_bots,
    unless_reviewers,
    validate_any,
    validate_item_owner,
    validate_input_data,
    validate_input_data_from_resolved_model,
    validate_patch_data,
    validate_data_documents,
)
from openprocurement.api.utils import context_unpack


def resolve_complaint(request, context="tender"):
    match_dict = request.matchdict
    if complaint_id := match_dict.get("complaint_id"):
        complaints = get_items(request, request.validated[context], "complaints", complaint_id)
        request.validated["complaint"] = complaints[0]


class BaseComplaintResource(TenderBaseResource):
    state_class = ComplaintState
    serializer_class = ComplaintSerializer

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_complaint"),
            (Allow, "g:brokers", "edit_complaint"),
            (Allow, "g:bots", "edit_complaint"),
            (Allow, "g:Administrator", "edit_complaint"),
            (Allow, "g:aboveThresholdReviewers", "edit_complaint"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl


class BaseComplaintGetResource(BaseComplaintResource):

    item_name = "tender"

    @json_view(permission="view_tender")
    def collection_get(self):
        """List complaints
        """
        context = self.request.validated[self.item_name]
        data = tuple(self.serializer_class(i).data for i in context.get("complaints", []))
        return {"data": data}

    @json_view(permission="view_tender")
    def get(self):
        """Retrieving the complaint
        """
        data = self.serializer_class(self.request.validated["complaint"]).data
        return {"data": data}


class BaseTenderComplaintGetResource(BaseComplaintGetResource):
    serializer_class = TenderComplaintSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_complaint(request)


class BaseComplaintWriteResource(BaseComplaintResource):
    serializer_class = TenderComplaintSerializer
    item_name = "tender"  # tender, cancellation or award

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
            validate_input_data(PostComplaint),
            validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"complaint_id": "__new__"})

        context = self.request.validated[self.item_name]
        tender = self.request.validated["tender"]
        complaint = self.request.validated["data"]
        access = set_ownership(complaint, self.request)

        claim_number = calculate_total_complaints(tender) + 1
        complaint["complaintID"] = f"{tender['tenderID']}.{self.request.registry.server_id}{claim_number}"

        self.state.validate_complaint_on_post(complaint)
        if "complaints" not in context:
            context["complaints"] = []
        context["complaints"].append(complaint)
        self.state.complaint_on_post(complaint)

        if save_tender(self.request):
            LOGGER.info(
                f"Created {self.item_name} complaint {complaint['id']}",
                extra=context_unpack(self.request,
                                     {"MESSAGE_ID": f"{self.item_name}_complaint_create"},
                                     {"complaint_id": complaint["id"]}),
            )
            self.request.response.status = 201

            route_params = dict(
                tender_id=tender["_id"],
                complaint_id=complaint["id"],
            )
            if self.item_name != "tender":
                route_params[f"{self.item_name}_id"] = context["id"]
                route_name = f"{tender['procurementMethodType']}:Tender {self.item_name.capitalize()} Complaints Get"
            else:
                route_name = f"{tender['procurementMethodType']}:Tender Complaints Get"
            self.request.response.headers["Location"] = self.request.route_url(route_name, **route_params)

            return {"data": self.serializer_class(complaint).data, "access": access}

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(
                unless_bots(
                    unless_reviewers(
                        validate_any(
                            validate_item_owner("tender"),
                            validate_item_owner("complaint"),
                        )
                    )
                )
            ),
            validate_input_data_from_resolved_model(),
            validate_patch_data(Complaint, item_name="complaint"),
        ),
        permission="edit_complaint",
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            complaint = self.request.validated["complaint"]
            self.state.validate_complaint_on_patch(complaint, updated)

            context = self.request.validated[self.item_name]

            set_item(context, "complaints", complaint["id"], updated)
            self.state.complaint_on_patch(complaint, updated)

            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated {self.item_name} complaint {complaint['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.item_name}_complaint_patch"}),
                )
                return {"data": self.serializer_class(updated).data}


class TenderComplaintResource(BaseComplaintWriteResource):
    serializer_class = ComplaintSerializer

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_complaint(request)
