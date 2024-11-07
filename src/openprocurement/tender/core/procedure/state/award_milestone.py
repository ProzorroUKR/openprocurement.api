from datetime import timedelta
from logging import getLogger

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneCodes,
)
from openprocurement.tender.core.procedure.state.qualification_milestone import (
    QualificationMilestoneState,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_tender_full_date

LOGGER = getLogger(__name__)


class AwardMilestoneState(QualificationMilestoneState):
    allowed_milestone_codes = (
        AwardMilestoneCodes.CODE_24_HOURS.value,
        AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value,
    )

    def validate_post(self, context_name, parent, milestone):
        super().validate_post(context_name, parent, milestone)
        if milestone["code"] not in self.allowed_milestone_codes:
            raise_operation_error(
                get_request(),
                [{"milestones": [f"Forbidden to add milestone with code {milestone['code']}"]}],
                status=422,
                name=f"{context_name}s",
            )
        if milestone["code"] == AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value:
            if parent.get("period"):
                parent_period_start_date = dt_from_iso(parent["period"]["startDate"])
                parent["period"]["endDate"] = milestone["dueDate"] = calculate_tender_full_date(
                    parent_period_start_date,
                    timedelta(days=20),
                    tender=get_tender(),
                    working_days=True,
                ).isoformat()
            else:
                raise_operation_error(
                    get_request(),
                    [
                        {
                            "milestones": [
                                f"Forbidden to add milestone with code {milestone['code']} for award without period"
                            ]
                        }
                    ],
                    name=f"{context_name}s",
                )


class AwardExtensionMilestoneState(AwardMilestoneState):
    allowed_milestone_codes = (AwardMilestoneCodes.CODE_EXTENSION_PERIOD.value,)
