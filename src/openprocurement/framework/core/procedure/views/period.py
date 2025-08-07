from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import context_unpack, json_view, update_logging_context
from openprocurement.framework.core.procedure.models.period import PostPeriodChange
from openprocurement.framework.core.procedure.serializers.period import (
    PeriodChangeSerializer,
)
from openprocurement.framework.core.procedure.state.period import PeriodChangeState
from openprocurement.framework.core.procedure.validation import (
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource


class CorePeriodChangeResource(FrameworkBaseResource):
    serializer_class = PeriodChangeSerializer
    state_class = PeriodChangeState

    @json_view(
        content_type="application/json",
        permission="edit_framework",
        validators=(
            validate_item_owner("framework"),
            validate_input_data(PostPeriodChange),
            validate_action_in_not_allowed_framework_status("period change"),
        ),
    )
    def post(self):
        update_logging_context(self.request, {"period_change_id": "__new__"})

        framework = self.request.validated["framework"]
        period_change = self.request.validated["data"]
        self.state.validate_period_change_on_post(period_change, framework)
        self.state.on_post(period_change, framework)

        self.save_all_objects()
        self.LOGGER.info(
            f"Created framework period change {period_change['id']}",
            extra=context_unpack(
                self.request,
                {"MESSAGE_ID": "framework_period_change_create"},
                {"framework_id": framework["_id"], "period_change_id": period_change["id"]},
            ),
        )
        self.request.response.status = 201
        self.request.response.headers["Location"] = self.request.route_url(
            f"{framework['frameworkType']}:Framework Period Change",
            framework_id=framework["_id"],
            period_change_id=period_change["id"],
        )
        return {"data": self.serializer_class(period_change).data}
