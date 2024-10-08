from logging import getLogger

from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.procedure.utils import get_items, set_item
from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import context_unpack, json_view
from openprocurement.tender.core.procedure.models.cancellation import (
    Cancellation,
    PatchCancellation,
    PostCancellation,
)
from openprocurement.tender.core.procedure.serializers.cancellation import (
    CancellationSerializer,
)
from openprocurement.tender.core.procedure.serializers.tender import (
    TenderBaseSerializer,
)
from openprocurement.tender.core.procedure.state.cancellation import CancellationState
from openprocurement.tender.core.procedure.utils import save_tender
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.utils import (
    ProcurementMethodTypePredicate,
    context_view,
)

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
        ),
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
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_cancellation_create"},
                    {"cancellation_id": cancellation["id"]},
                ),
            )
            self.request.response.status = 201
            route_prefix = ProcurementMethodTypePredicate.route_prefix(self.request)
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender Cancellations".format(route_prefix),
                tender_id=tender["_id"],
                cancellation_id=cancellation["id"],
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
    @context_view(
        objs={
            "tender": TenderBaseSerializer,
        }
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
        ),
    )
    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            cancellation = self.request.validated["cancellation"]
            self.state.validate_cancellation_patch(cancellation, updated)
            set_item(
                self.request.validated["tender"],
                "cancellations",
                cancellation["id"],
                updated,
            )
            self.state.cancellation_on_patch(cancellation, updated)
            if save_tender(self.request):
                self.LOGGER.info(
                    f"Updated tender cancellation {cancellation['id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "tender_cancellation_patch"}),
                )
                return {"data": self.serializer_class(updated).data}
