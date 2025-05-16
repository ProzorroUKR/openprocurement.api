from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.tender.core.procedure.models.complaint_appeal import (
    Appeal,
    PatchAppeal,
    PostAppeal,
)
from openprocurement.tender.core.procedure.serializers.complaint_appeal import (
    ComplaintAppealSerializer,
)
from openprocurement.tender.core.procedure.state.complaint_appeal import (
    ComplaintAppealState,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import validate_any
from openprocurement.tender.core.procedure.views.complaint import (
    BaseComplaintResource,
    resolve_complaint,
)
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate


def resolve_complaint_appeal(request, context="complaint"):
    match_dict = request.matchdict
    if appeal_id := match_dict.get("appeal_id"):
        complaints = get_items(request, request.validated[context], "appeals", appeal_id)
        request.validated["appeal"] = complaints[0]


class BaseComplaintAppealResource(BaseComplaintResource):
    serializer_class = ComplaintAppealSerializer
    state_class = ComplaintAppealState
    item_name = "tender"

    @json_view(
        content_type="application/json",
        permission="edit_complaint",
        validators=(
            validate_any(
                validate_item_owner("complaint"),
                validate_item_owner("tender"),
            ),
            validate_input_data(PostAppeal),
            validate_data_documents(route_key="appeal_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"appeal_id": "__new__"})

        tender = self.request.validated["tender"]
        context = self.request.validated[self.item_name]  # tender, award, cancellation, qualification
        complaint = self.request.validated["complaint"]
        appeal = self.request.validated["data"]

        if "appeals" not in complaint:
            complaint["appeals"] = []
        complaint["appeals"].append(appeal)
        self.state.complaint_appeal_on_post(appeal)

        if save_tender(self.request):
            kwargs = {
                "tender_id": tender["_id"],
                "complaint_id": complaint["id"],
                "appeal_id": appeal["id"],
            }
            if self.item_name != "tender":
                kwargs[f"{self.item_name}_id"] = context["id"]
            self.LOGGER.info(
                f"Created appeal {appeal['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": f"{self.item_name}_complaint_appeal_create"},
                    kwargs,
                ),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            extended_item_name = f"Tender {self.item_name.capitalize()}" if self.item_name != "tender" else "Tender"
            self.request.response.headers["Location"] = self.request.route_url(
                f"{route_prefix}:{extended_item_name} Complaint Appeals", **kwargs
            )
            return {"data": self.serializer_class(appeal).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        complaint = self.request.validated["complaint"]
        data = [self.serializer_class(b).data for b in complaint.get("appeals", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["appeal"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_any(
                validate_item_owner("tender"),
                validate_item_owner("complaint"),
            ),
            validate_input_data(PatchAppeal),
            validate_patch_data(Appeal, item_name="appeal"),
        ),
        permission="edit_complaint",
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            appeal = self.request.validated["appeal"]
            complaint = self.request.validated["complaint"]

            set_item(complaint, "appeals", appeal["id"], updated)
            self.state.complaint_appeal_on_patch(appeal, updated)

            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated {self.item_name} complaint appeal {appeal['id']}",
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": f"{self.item_name}_complaint_appeal_patch"},
                    ),
                )
                return {"data": self.serializer_class(updated).data}


class BaseTenderComplaintAppealResource(BaseComplaintAppealResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_complaint(request)
        resolve_complaint_appeal(request)
