from datetime import timedelta
from logging import getLogger

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from openprocurement.api.constants import FRAMEWORK_CONFIG_JSONSCHEMAS
from openprocurement.api.context import get_now, get_request
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import context_unpack, raise_operation_error
from openprocurement.framework.core.constants import (
    ENQUIRY_PERIOD_DURATION,
    ENQUIRY_STAND_STILL_TIME,
    MAX_QUALIFICATION_DURATION,
    MIN_QUALIFICATION_DURATION,
    SUBMISSION_STAND_STILL_DURATION,
)
from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.core.procedure.state.chronograph import (
    ChronographEventsMixing,
)
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.core.procedure.utils import (
    get_framework_unsuccessful_status_check_date,
    save_object,
)
from openprocurement.framework.core.utils import calculate_framework_date
from openprocurement.tender.core.procedure.utils import dt_from_iso

AGREEMENT_DEPENDENT_FIELDS = ("qualificationPeriod", "procuringEntity")
LOGGER = getLogger(__name__)


class FrameworkConfigMixin:
    configurations = ("restrictedDerivatives", "qualificationComplainDuration")

    def validate_config(self, data):
        for config_name in self.configurations:
            value = data["config"].get(config_name)
            framework_type = data.get("frameworkType")
            config_schema = FRAMEWORK_CONFIG_JSONSCHEMAS.get(framework_type)
            if not config_schema:
                raise NotImplementedError
            schema = config_schema["properties"][config_name]
            try:
                validate(value, schema)
            except ValidationError as e:
                raise_operation_error(
                    self.request,
                    e.message,
                    status=422,
                    location="body",
                    name=config_name,
                )


class FrameworkState(BaseState, FrameworkConfigMixin, ChronographEventsMixing):
    agreement_class = AgreementState
    qualification_class = QualificationState
    submission_class = SubmissionState

    def __init__(self, request):
        super().__init__(request)
        self.agreement = self.agreement_class(request, framework=self)
        self.qualification = self.qualification_class(request, framework=self)
        self.submission = self.submission_class(request, framework=self)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def always(self, data):
        self.update_next_check(data)

    def on_post(self, data):
        self.validate_config(data)
        data["date"] = get_now().isoformat()
        if data["config"].get("test"):
            data["mode"] = "test"
        if data.get("procuringEntity", {}).get("kind") == "defense":
            data["config"]["restrictedDerivatives"] = True
        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_on_patch(before, after)
        self.validate_framework_patch_status(after)
        super().on_patch(before, after)

    def after_patch(self, data):
        if (
            any(field in data for field in AGREEMENT_DEPENDENT_FIELDS)
            and data.get("agreementID")
            and get_request().validated["agreement_src"]["status"] == "active"
        ):
            self.update_agreement(data)

    def get_next_check(self, data):
        checks = []
        if data["status"] == "active":
            if not data.get("successful"):
                unsuccessful_status_check = get_framework_unsuccessful_status_check_date(data)
                if unsuccessful_status_check:
                    checks.append(unsuccessful_status_check)
            checks.append(dt_from_iso(data["qualificationPeriod"]["endDate"]))
        return min(checks).isoformat() if checks else None

    def validate_on_patch(self, before, after):
        status = after.get("status")
        if status not in ("draft", "active"):
            raise_operation_error(
                get_request(),
                f"Can't switch to {status} status",
            )
        if status == "active":
            self.calculate_framework_periods(after)
            self.validate_qualification_period_duration(
                before,
                after,
                MIN_QUALIFICATION_DURATION,
                MAX_QUALIFICATION_DURATION,
            )

    def validate_framework_patch_status(self, data):
        framework_status = data.get("status")
        if get_request().authenticated_role != "Administrator" and framework_status not in ("draft", "active"):
            raise_operation_error(get_request(), f"Can't update framework in current ({framework_status}) status")

    def update_agreement(self, data):
        agreement_data = get_request().validated["agreement"]

        end_date = data["qualificationPeriod"]["endDate"]

        agreement_data.update(
            {
                "period": {
                    "startDate": agreement_data["period"]["startDate"],
                    "endDate": end_date,
                },
                "procuringEntity": data["procuringEntity"],
                "contracts": agreement_data["contracts"],
            }
        )
        for contract in agreement_data["contracts"]:
            for milestone in contract["milestones"]:
                if milestone["type"] == "activation":
                    milestone["dueDate"] = end_date

        if save_object(get_request(), "agreement"):
            LOGGER.info(
                f"Updated agreement {agreement_data['_id']}",
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "framework_patch"},
                ),
            )

    def validate_qualification_period_duration(self, before, after, min_duration, max_duration):
        if before["status"] == "active" and before["qualificationPeriod"] == after["qualificationPeriod"]:
            # There is a cases when qualificationPeriod in active frameworks
            # where changed outside the api to prolong the framework.
            # In this case we should not validate the qualificationPeriod duration
            # if it was not changed in this request.
            # So, skip the validation.
            return

        start_date = dt_from_iso(after["qualificationPeriod"]["startDate"])
        end_date = dt_from_iso(after["qualificationPeriod"]["endDate"])

        end_date_min = calculate_framework_date(start_date, timedelta(days=min_duration), after)
        if end_date_min > end_date:
            raise_operation_error(
                get_request(), f"qualificationPeriod must be at least {min_duration} full calendar days long"
            )

        end_date_max = calculate_framework_date(start_date, timedelta(days=max_duration), after, ceil=True)
        if end_date_max < end_date:
            raise_operation_error(
                get_request(), f"qualificationPeriod must be less than {max_duration} full calendar days long"
            )

    def calculate_framework_periods(self, data):
        now = get_now()
        if enquiry_start := data.get("enquiryPeriod", {}).get("startDate"):
            enquiry_period_start_date = dt_from_iso(enquiry_start)
        else:
            enquiry_period_start_date = now

        if enquiry_end := data.get("enquiryPeriod", {}).get("endDate"):
            enquiry_period_end_date = dt_from_iso(enquiry_end)
        else:
            enquiry_period_end_date = calculate_framework_date(
                enquiry_period_start_date,
                timedelta(days=ENQUIRY_PERIOD_DURATION),
                data,
                working_days=True,
                ceil=True,
            )

        clarifications_until = calculate_framework_date(
            enquiry_period_end_date,
            timedelta(days=ENQUIRY_STAND_STILL_TIME),
            data,
            working_days=True,
        )

        data["enquiryPeriod"] = {
            "startDate": enquiry_period_start_date.isoformat(),
            "endDate": enquiry_period_end_date.isoformat(),
            "clarificationsUntil": clarifications_until.isoformat(),
        }

        qualification_end_date = dt_from_iso(data["qualificationPeriod"]["endDate"])
        if period_start := data.get("period", {}).get("startDate"):
            period_start_date = dt_from_iso(period_start)
        else:
            period_start_date = now
        period_end_date = calculate_framework_date(
            qualification_end_date,
            timedelta(days=-SUBMISSION_STAND_STILL_DURATION),
            data,
        )
        data["period"] = {
            "startDate": period_start_date.isoformat(),
            "endDate": period_end_date.isoformat(),
        }

        data["qualificationPeriod"]["startDate"] = enquiry_period_start_date.isoformat()
