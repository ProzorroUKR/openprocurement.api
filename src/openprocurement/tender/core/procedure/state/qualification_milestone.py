from datetime import timedelta
from logging import getLogger

from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import validate_tender_first_revision_date
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.qualification_milestone import (
    PostQualificationMilestone,
    QualificationMilestoneCode,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_date

LOGGER = getLogger(__name__)


class QualificationMilestoneState(BaseState):
    post_data_model = PostQualificationMilestone

    # milestones exist since RELEASE_2020_04_19 (limited: not checked)
    milestone_post_release_check = True
    # rfp: the user may set a dueDate later than 24h (24h is only the minimum)
    milestone_24h_due_date_extendable = False
    milestone_post_allowed_tender_statuses: tuple = ("active.pre-qualification",)
    milestone_post_requires_active_lot = True

    def validate_milestone_post_request(self):
        self.validate_item_owner("tender")
        if self.milestone_post_release_check:
            validate_tender_first_revision_date(self.request, validation_date=RELEASE_2020_04_19)
        self.validate_input_data(self.get_post_data_model())

    def get_24h_milestone_dueDate(self, milestone):
        min_due_date = calculate_tender_date(
            dt_from_iso(milestone["date"]),
            timedelta(hours=24),
            tender=get_tender(),
        ).isoformat()
        if self.milestone_24h_due_date_extendable:
            return max(min_due_date, milestone.get("dueDate", min_due_date))
        return min_due_date

    def validate_post_allowed(self, context_name, parent):
        tender = get_tender()
        if tender["status"] not in self.milestone_post_allowed_tender_statuses:
            raise_operation_error(
                get_request(),
                f"Can't update {context_name} in current ({tender['status']}) tender status",
            )
        if self.milestone_post_requires_active_lot and any(
            lot.get("status") != "active" for lot in tender.get("lots", "") if lot.get("id") == parent.get("lotID")
        ):
            raise_operation_error(get_request(), f"Can update {context_name} only in active lot status")

    def validate_post(self, context_name, parent, milestone):
        self.validate_post_allowed(context_name, parent)
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
