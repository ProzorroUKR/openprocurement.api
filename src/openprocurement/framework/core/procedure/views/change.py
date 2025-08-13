from openprocurement.api.procedure.utils import get_items
from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.framework.core.procedure.models.change import PostChange
from openprocurement.framework.core.procedure.serializers.change import ChangeSerializer
from openprocurement.framework.core.procedure.serializers.framework import (
    FrameworkSerializer,
)
from openprocurement.framework.core.procedure.state.change import ChangeState
from openprocurement.framework.core.procedure.validation import (
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.tender.core.utils import context_view


def resolve_change(request):
    match_dict = request.matchdict
    if match_dict.get("change_id"):
        change_id = match_dict["change_id"]
        changes = get_items(request, request.validated["framework"], "changes", change_id)
        request.validated["change"] = changes[0]


class CoreChangeResource(FrameworkBaseResource):
    serializer_class = ChangeSerializer
    state_class = ChangeState

    def __init__(self, request, context=None):
        super().__init__(request, context)
        if context and request.matchdict:
            resolve_change(request)

    @json_view(permission="view_framework")
    def collection_get(self):
        """
        List changes
        """
        framework = self.request.validated["framework"]
        data = tuple(self.serializer_class(change, framework=framework).data for change in framework.get("changes", []))
        return {"data": data}

    @json_view(permission="view_framework")
    @context_view(
        objs={
            "framework": (FrameworkSerializer, None),
        }
    )
    def get(self):
        """
        Retrieving the question
        """
        framework = self.request.validated["framework"]
        change = self.request.validated["change"]
        data = self.serializer_class(change, framework=framework).data
        return {"data": data}

    @json_view(
        content_type="application/json",
        permission="edit_framework",
        validators=(
            validate_item_owner("framework"),
            validate_input_data(PostChange),
            validate_action_in_not_allowed_framework_status("change"),
        ),
    )
    def collection_post(self):
        update_logging_context(self.request, {"change_id": "__new__"})

        framework = self.request.validated["framework"]
        change = self.request.validated["data"]
        self.state.validate_change_on_post(change, framework)
        self.state.on_post(change, framework)

        self.save_all_objects()
        self.LOGGER.info(
            f"Created framework change {change['id']}",
            extra=context_unpack(
                self.request,
                {"MESSAGE_ID": "framework_change_create"},
                {"framework_id": framework["_id"], "change_id": change["id"]},
            ),
        )
        self.request.response.status = 201
        self.request.response.headers["Location"] = self.request.route_url(
            f"{framework['frameworkType']}:Framework Change",
            framework_id=framework["_id"],
            change_id=change["id"],
        )
        return {"data": self.serializer_class(change).data}
