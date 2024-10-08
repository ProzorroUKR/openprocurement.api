from pyramid.security import Allow, Everyone

from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.tender.core.procedure.models.review_request import (
    PatchInspectorReviewRequest,
    PostInspectorReview,
    ReviewRequest,
)
from openprocurement.tender.core.procedure.state.review_request import (
    ReviewRequestState,
)
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.utils import ProcurementMethodTypePredicate


def resolve_review_request(request):
    match_dict = request.matchdict
    if match_dict.get("review_request_id"):
        review_request_id = match_dict["review_request_id"]
        review_request = get_items(request, request.validated["tender"], "reviewRequests", review_request_id)
        request.validated["review_request"] = review_request[0]


class TenderReviewRequestResource(TenderBaseResource):
    serializer_class = BaseSerializer
    state_class = ReviewRequestState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_review_request"),
            (Allow, "g:inspectors", "edit_review_request"),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_review_request(request)

    @json_view(
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostInspectorReview),
        ),
        permission="create_review_request",
    )
    def collection_post(self):
        update_logging_context(self.request, {"review_request_id": "__new__"})

        tender = self.request.validated["tender"]
        review_request = self.request.validated["data"]
        self.state.review_request_on_post(review_request)
        if "reviewRequests" not in tender:
            tender["reviewRequests"] = []
        tender["reviewRequests"].append(review_request)

        self.state.always(self.request.validated["tender"])

        if save_tender(self.request):
            self.LOGGER.info(
                f"Created tender review request {review_request['id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_review_request_create"},
                    {"review_request_id": review_request["id"]},
                ),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Review Request".format(route_prefix),
                tender_id=tender["_id"],
                review_request_id=review_request["id"],
            )
            return {"data": self.serializer_class(review_request).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        data = [self.serializer_class(b).data for b in tender.get("reviewRequests", "")]
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["review_request"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="edit_review_request",
        validators=(
            validate_input_data(PatchInspectorReviewRequest),
            validate_patch_data_simple(ReviewRequest, item_name="review_request"),
        ),
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            review_request = self.request.validated["review_request"]

            set_item(
                self.request.validated["tender"],
                "reviewRequests",
                review_request["id"],
                updated,
            )

            self.state.review_request_on_patch(review_request, updated)
            self.state.always(self.request.validated["tender"])
            if save_tender(self.request):
                self.LOGGER.info(
                    "Updated tender review request {}".format(review_request["id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_review_request_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
