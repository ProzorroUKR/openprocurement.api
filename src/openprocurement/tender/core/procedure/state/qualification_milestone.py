from logging import getLogger

from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request

LOGGER = getLogger(__name__)


class QualificationMilestoneState(BaseState):
    def validate_post(self, context_name, parent, milestone):
        parent_status = parent.get("status")
        if parent_status != "pending":
            raise_operation_error(get_request(), f"Not allowed in current '{parent_status}' {context_name} status")

        # for now milestones CODE_24_HOURS and CODE_EXTENSION_PERIOD could be only one
        if any(m.get("code") == milestone["code"] for m in parent.get("milestones", "")):
            raise_operation_error(
                get_request(),
                [{"milestones": [f"There can be only one '{milestone['code']}' milestone"]}],
                status=422,
                name=f"{context_name}s",
            )
