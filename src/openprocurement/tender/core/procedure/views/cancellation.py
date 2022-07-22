from openprocurement.tender.core.procedure.utils import get_items
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.api.utils import json_view, context_unpack
from openprocurement.tender.core.procedure.utils import save_tender, set_item
from openprocurement.tender.core.procedure.serializers.cancellation import CancellationSerializer
from openprocurement.tender.core.procedure.models.cancellation import PostCancellation, PatchCancellation, Cancellation
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    unless_admins,
    validate_data_documents,
)
from openprocurement.tender.core.procedure.state.cancellation import CancellationState
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from logging import getLogger

LOGGER = getLogger(__name__)


def resolve_cancellation(request):
    match_dict = request.matchdict
    if match_dict.get("cancellation_id"):
        cancellation_id = match_dict["cancellation_id"]
        cancellations = get_items(request, request.validated["tender"], "cancellations", cancellation_id)
        request.validated["cancellation"] = cancellations[0]


class BaseCancellationResource(TenderBaseResource):

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_tender"),
            (Allow, "g:brokers", "create_cancellation"),
            (Allow, "g:brokers", "edit_cancellation"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    serializer_class = CancellationSerializer
    state_class = CancellationState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_cancellation(request)

    @json_view(
        content_type="application/json",
        permission="create_cancellation",
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PostCancellation),
        )
    )
    def collection_post(self):
        tender = self.request.validated["tender"]
        cancellation = self.request.validated["data"]

        self.state.validate_cancellation_post(cancellation)

        if "cancellations" not in tender:
            tender["cancellations"] = []
        tender["cancellations"].append(cancellation)

        self.state.cancellation_on_post(cancellation)

        if save_tender(self.request):
            LOGGER.info(
                "Created tender cancellation {}".format(cancellation["id"]),
                extra=context_unpack(self.request,
                                     {"MESSAGE_ID": "tender_cancellation_create"},
                                     {"cancellation_id": cancellation["id"]}),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Cancellations".format(tender["procurementMethodType"]),
                tender_id=tender["_id"], cancellation_id=cancellation["id"]
            )
            return {"data": self.serializer_class(cancellation).data}

    @json_view(
        permission="view_tender",
    )
    def collection_get(self):
        tender = self.request.validated["tender"]
        data = tuple(self.serializer_class(b).data for b in tender.get("cancellations", ""))
        return {"data": data}

    @json_view(
        permission="view_tender",
    )
    def get(self):
        data = self.serializer_class(self.request.validated["cancellation"]).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="edit_cancellation",
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(PatchCancellation),
            validate_patch_data_simple(Cancellation, item_name="cancellation"),
        )
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            cancellation = self.request.validated["cancellation"]
            self.state.validate_cancellation_patch(cancellation, updated)
            set_item(self.request.validated["tender"], "cancellations", cancellation["id"], updated)
            self.state.cancellation_on_patch(cancellation, updated)
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender cancellation {cancellation['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_patch"}),
                )
                return {"data": self.serializer_class(updated).data}

