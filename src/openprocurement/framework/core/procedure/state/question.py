from logging import getLogger

from openprocurement.api.context import get_now, get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class QuestionState(BaseState):

    def validate_question_on_post(self):
        self.validate_framework_question_operation_not_in_allowed_status()
        self.validate_framework_question_operation_not_in_enquiry_period()

    def on_patch(self, before, after):
        self.validate_question_clarifications_until()
        self.validate_framework_question_operation_not_in_allowed_status()
        after["dateAnswered"] = get_now().isoformat()
        super().on_patch(before, after)

    def validate_framework_question_operation_not_in_allowed_status(self):
        if get_request().validated["framework"].get("status") != "active":
            raise_operation_error(
                get_request(),
                f"Can't {OPERATIONS.get(get_request().method)} question in current "
                f"({get_request().validated['framework']['status']}) framework status"
            )

    def validate_framework_question_operation_not_in_enquiry_period(self):
        framework = get_request().validated["framework"]
        enquiry_period = framework.get("enquiryPeriod")
        now = get_now()

        if (
            not enquiry_period
            or "startDate" not in enquiry_period
            or "endDate" not in enquiry_period
            or now < dt_from_iso(enquiry_period["startDate"])
            or now > dt_from_iso(enquiry_period["endDate"])
        ):
            raise_operation_error(
                get_request(),
                f"Question can be add only during the enquiry period: "
                f"from ({enquiry_period['startDate']}) to ({enquiry_period['endDate']}).",
            )

    def validate_question_clarifications_until(self):
        now = get_now()
        framework = get_request().validated["framework"]
        if clarifications_until := framework.get("enquiryPeriod", {}).get("clarificationsUntil"):
            if now > dt_from_iso(clarifications_until):
                raise_operation_error(
                    get_request(),
                    "Allowed to update question only before enquiryPeriod.clarificationsUntil",
                )
