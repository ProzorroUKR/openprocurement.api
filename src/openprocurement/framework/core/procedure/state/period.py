from datetime import timedelta
from logging import getLogger

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.core.constants import (
    MAX_QUALIFICATION_DURATION,
    SUBMISSION_STAND_STILL_DURATION,
)
from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.utils import calculate_framework_full_date
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class PeriodChangeState(FrameworkState):
    agreement_class = AgreementState

    def validate_period_change_on_post(self, data, framework):
        self.validate_period(data, framework)

    def on_post(self, data, framework):
        new_period = data.pop("qualificationPeriod", None)
        data.update(
            {
                "prevPeriodEndDate": framework["qualificationPeriod"]["endDate"],
                "newPeriodEndDate": new_period["endDate"],
                "date": get_request_now().isoformat(),
            }
        )
        if "periodChangeHistory" not in framework:
            framework["periodChangeHistory"] = []
        framework["periodChangeHistory"].append(data)
        framework["qualificationPeriod"]["endDate"] = new_period["endDate"]
        # recalculate next_check and other objects periods after qualificationPeriod was changed
        self.calculate_framework_periods(framework)
        self.update_agreement(framework)
        self.update_next_check(framework)
        if agreement := self.request.validated.get("agreement"):
            self.agreement_class(self.request, framework=framework).update_next_check(agreement)

    def validate_period(self, data, framework):
        if (
            data.get("qualificationPeriod", {}).get("startDate")
            and data["qualificationPeriod"]["startDate"] != framework["qualificationPeriod"]["startDate"]
        ):
            raise_operation_error(
                get_request(),
                "Forbidden to change qualification period start date",
                status=422,
                name="qualificationPeriod",
            )
        start_date = get_request_now()
        end_date = dt_from_iso(data["qualificationPeriod"]["endDate"])

        end_date_min = calculate_framework_full_date(
            start_date,
            timedelta(days=SUBMISSION_STAND_STILL_DURATION),
            framework=framework,
        )
        if end_date_min > end_date:
            raise_operation_error(
                get_request(),
                f"qualificationPeriod.endDate couldn't be less than "
                f"{SUBMISSION_STAND_STILL_DURATION} full days from now",
                status=422,
                name="qualificationPeriod",
            )

        end_date_max = calculate_framework_full_date(
            start_date,
            timedelta(days=MAX_QUALIFICATION_DURATION),
            framework=framework,
            ceil=True,
        )
        if end_date_max < end_date:
            raise_operation_error(
                get_request(),
                f"qualificationPeriod.endDate couldn't be more than {MAX_QUALIFICATION_DURATION} full days from now",
                status=422,
                name="qualificationPeriod",
            )
