from datetime import timedelta
from logging import getLogger

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.qualification_milestone import QualificationMilestoneCode
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_date

LOGGER = getLogger(__name__)


class QualificationMilestoneState(BaseState):
    def get_24h_milestone_dueDate(self, milestone):
        return calculate_tender_date(
            dt_from_iso(milestone["date"]),
            timedelta(hours=24),
            tender=get_tender(),
        ).isoformat()

    def validate_post(self, context_name, parent, milestone):
        parent_status = parent.get("status")
        if parent_status != "pending":
            raise_operation_error(
                get_request(),
                f"Not allowed in current '{parent_status}' {context_name} status",
            )

        # for now milestones CODE_24_HOURS and CODE_EXTENSION_PERIOD could be only one
        if any(m.get("code") == milestone["code"] for m in parent.get("milestones", "")):
            raise_operation_error(
                get_request(),
                [{"milestones": [f"There can be only one '{milestone['code']}' milestone"]}],
                status=422,
                name=f"{context_name}s",
            )

        if milestone["code"] == QualificationMilestoneCode.CODE_24_HOURS.value:
            milestone["dueDate"] = self.get_24h_milestone_dueDate(milestone)
