from copy import deepcopy
from datetime import timedelta
from logging import getLogger

from openprocurement.api.constants import FRAMEWORK_CONFIG_JSONSCHEMAS
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.state.base import BaseState, ConfigMixin
from openprocurement.api.procedure.validation import (
    validate_items_classifications_prefixes,
)
from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.core.constants import (
    ENQUIRY_PERIOD_DURATION,
    MAX_QUALIFICATION_DURATION,
    MIN_QUALIFICATION_DURATION,
    SUBMISSION_STAND_STILL_DURATION,
)
from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.core.procedure.state.chronograph import (
    FrameworkChronographEventsMixing,
)
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.core.utils import calculate_framework_full_date
from openprocurement.tender.core.procedure.utils import dt_from_iso

AGREEMENT_DEPENDENT_FIELDS = (
    "qualificationPeriod",
    "procuringEntity",
)
LOGGER = getLogger(__name__)


class FrameworkConfigMixin(ConfigMixin):
    def get_config_schema(self, data):
        framework_type = data.get("frameworkType")
        config_schema = FRAMEWORK_CONFIG_JSONSCHEMAS.get(framework_type)

        if not config_schema:
            # frameworkType not found in FRAMEWORK_CONFIG_JSONSCHEMAS
            raise NotImplementedError

        config_schema = deepcopy(config_schema)

        return config_schema

    def on_post(self, data):
        self.validate_config(data)
        super().on_post(data)

    def validate_config(self, data):
        # load schema from standards
        config_schema = self.get_config_schema(data)

        # do not validate required fields
        config_schema.pop("required", None)

        # common validation
        super().validate_config(data)


class FrameworkState(BaseState, FrameworkConfigMixin, FrameworkChronographEventsMixing):
    agreement_class = AgreementState
    qualification_class = QualificationState
    submission_class = SubmissionState
    working_days = True

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
        data["date"] = get_request_now().isoformat()
        self.validate_items_presence(data)
        self.validate_items_classification_prefix(data)
        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_on_patch(before, after)
        self.validate_items_presence(after)
        self.validate_items_classification_prefix(after)
        self.validate_framework_patch_status(before)
        self.update_agreement(after)
        super().on_patch(before, after)

    def get_next_check(self, data):
        checks = []
        if data["status"] == "active":
            if not data.get("successful"):
                unsuccessful_status_check = self.get_unsuccessful_status_check_date(data)
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

    def validate_items_presence(self, data):
        # Items are not allowed for framework with hasItems set to false
        if data["config"]["hasItems"] is False and data.get("items"):
            raise_operation_error(
                get_request(),
                "Items are not allowed for framework with hasItems set to false",
                status=422,
                name="items",
            )
        # Items are required for framework with hasItems set to true
        # Validate only on switch to active status or in active status to allow items manipulation in draft status
        if data["config"]["hasItems"] is True and not data.get("items") and data["status"] == "active":
            raise_operation_error(
                get_request(),
                "Items are required for framework with hasItems set to true",
                status=422,
                name="items",
            )

    def validate_framework_patch_status(self, data):
        framework_status = data.get("status")
        if get_request().authenticated_role != "Administrator" and framework_status not in ("draft", "active"):
            raise_operation_error(
                get_request(),
                f"Can't update framework in current ({framework_status}) status",
            )

    def update_agreement(self, data):
        if (
            any(field in data for field in AGREEMENT_DEPENDENT_FIELDS)
            and data.get("agreementID")
            and get_request().validated["agreement_src"]["status"] == "active"
        ):
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

    def validate_qualification_period_duration(self, before, after, min_duration, max_duration):
        if before["status"] == "active":
            # for active frameworks it is forbidden to modify qualificationPeriod directly.
            # There is /modify-period endpoint
            return

        start_date = dt_from_iso(after["qualificationPeriod"]["startDate"])
        end_date = dt_from_iso(after["qualificationPeriod"]["endDate"])

        end_date_min = calculate_framework_full_date(
            start_date,
            timedelta(days=min_duration),
            framework=after,
        )
        if end_date_min > end_date:
            raise_operation_error(
                get_request(),
                f"qualificationPeriod couldn't be less than {min_duration} full calendar days long",
            )

        end_date_max = calculate_framework_full_date(
            start_date,
            timedelta(days=max_duration),
            framework=after,
            ceil=True,
        )
        if end_date_max < end_date:
            raise_operation_error(
                get_request(),
                f"qualificationPeriod couldn't be more than {max_duration} full calendar days long",
            )

    def calculate_framework_periods(self, data):
        clarification_until_duration = data["config"]["clarificationUntilDuration"]
        now = get_request_now()
        if enquiry_start := data.get("enquiryPeriod", {}).get("startDate"):
            enquiry_period_start_date = dt_from_iso(enquiry_start)
        else:
            enquiry_period_start_date = now

        if enquiry_end := data.get("enquiryPeriod", {}).get("endDate"):
            enquiry_period_end_date = dt_from_iso(enquiry_end)
        else:
            enquiry_period_end_date = calculate_framework_full_date(
                enquiry_period_start_date,
                timedelta(days=ENQUIRY_PERIOD_DURATION),
                framework=data,
                working_days=True,
                ceil=True,
            )

        clarifications_until = calculate_framework_full_date(
            enquiry_period_end_date,
            timedelta(days=clarification_until_duration),
            framework=data,
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
        period_end_date = calculate_framework_full_date(
            qualification_end_date,
            timedelta(days=-SUBMISSION_STAND_STILL_DURATION),
            framework=data,
        )
        data["period"] = {
            "startDate": period_start_date.isoformat(),
            "endDate": period_end_date.isoformat(),
        }

        data["qualificationPeriod"] = {
            "startDate": enquiry_period_start_date.isoformat(),
            "endDate": data["qualificationPeriod"]["endDate"],
        }

    def validate_items_classification_prefix(self, framework):
        classifications = [item["classification"] for item in framework.get("items", "")]
        if not classifications:
            return
        validate_items_classifications_prefixes(classifications)
        validate_items_classifications_prefixes(
            classifications,
            root_classification=framework["classification"],
            root_name="framework",
        )
