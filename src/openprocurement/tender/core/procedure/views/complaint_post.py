from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.procedure.utils import get_items
from openprocurement.api.procedure.validation import (
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.tender.core.procedure.models.complaint_post import (
    CreateComplaintPost,
)
from openprocurement.tender.core.procedure.serializers.complaint_post import (
    ComplaintPostSerializer,
)
from openprocurement.tender.core.procedure.state.complaint_post import (
    ComplaintPostState,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.validation import (
    unless_reviewers,
    validate_any,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate


def resolve_complaint_post(request, context="complaint"):
    match_dict = request.matchdict
    if post_id := match_dict.get("post_id"):
        complaints = get_items(request, request.validated[context], "posts", post_id)
        request.validated["post"] = complaints[0]


class BaseComplaintPostResource(TenderBaseResource):
    serializer_class = ComplaintPostSerializer
    state_class = ComplaintPostState
    item_name = "tender"

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_complaint_post"),
            # (Allow, "g:Administrator", "edit_complaint"),
            (Allow, "g:aboveThresholdReviewers", "create_complaint_post"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    @json_view(
        content_type="application/json",
        permission="create_complaint_post",
        validators=(
            unless_reviewers(
                validate_any(
                    validate_item_owner("complaint"),
                    validate_item_owner("tender"),
                )
            ),
            validate_input_data(CreateComplaintPost),
            validate_data_documents(route_key="post_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"post_id": "__new__"})

        tender = self.request.validated["tender"]
        context = self.request.validated[self.item_name]  # tender, award, cancellation, qualification
        complaint = self.request.validated["complaint"]
        post = self.request.validated["data"]

        self.state.validate_complaint_post_on_post(post)
        if "posts" not in complaint:
            complaint["posts"] = []
        complaint["posts"].append(post)
        self.state.complaint_post_on_post(post)

        if save_tender(self.request):
            kwargs = {
                "tender_id": tender["_id"],
                "complaint_id": complaint["id"],
                "post_id": post["id"],
            }
            if self.item_name != "tender":
                kwargs[f"{self.item_name}_id"] = context["id"]
            self.LOGGER.info(
                f"Created post {post['id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": f"{self.item_name}_complaint_post_create"}, kwargs),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            extended_item_name = f"Tender {self.item_name.capitalize()}" if self.item_name != "tender" else "Tender"
            self.request.response.headers["Location"] = self.request.route_url(
                f"{route_prefix}:{extended_item_name} Complaint Posts", **kwargs
            )
            return {"data": self.serializer_class(post).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        complaint = self.request.validated["complaint"]
        data = [self.serializer_class(b).data for b in complaint.get("posts", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["post"]).data
        return {"data": data}


class BaseTenderComplaintPostResource(BaseComplaintPostResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_complaint(request)
        resolve_complaint_post(request)
