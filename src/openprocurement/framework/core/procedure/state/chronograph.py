from datetime import timedelta
from logging import getLogger

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.utils import context_unpack
from openprocurement.framework.core.constants import (
    AGREEMENT_TERMINATION_DETAILS_NOT_ENOUGH_SUBMISSIONS,
)
from openprocurement.framework.core.procedure.utils import (
    get_framework_number_of_submissions,
)
from openprocurement.framework.core.utils import calculate_framework_full_date
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class BaseChronographEventsMixing:
    def update_next_check(self, data):
        # next_check is field that shows object's expectation to be triggered at a certain time
        next_check = self.get_next_check(data)
        if next_check is not None:
            data["next_check"] = next_check
        elif "next_check" in data:
            del data["next_check"]

    def get_next_check(self, data):
        pass


class FrameworkChronographEventsMixing(BaseChronographEventsMixing):
    min_submissions_number = 3
    min_submissions_number_days = 15
    min_submissions_number_working_days = False

    def on_chronograph_patch(self, data):
        self.check_status(data)
        self.update_next_check(data)

    def check_status(self, framework):
        if framework.get("status") == "active":
            if not framework.get("successful"):
                unsuccessful_status_check = self.get_unsuccessful_status_check_date(framework)
                if unsuccessful_status_check and unsuccessful_status_check < get_request_now():
                    number_of_submissions = get_framework_number_of_submissions(get_request(), framework)
                    if number_of_submissions < self.min_submissions_number:
                        LOGGER.info(
                            f"Switched framework {framework['_id']} to unsuccessful",
                            extra=context_unpack(
                                get_request(),
                                {"MESSAGE_ID": "switched_framework_unsuccessful"},
                            ),
                        )
                        self.terminate_agreement()
                        framework["status"] = "unsuccessful"
                        return
                    else:
                        framework["successful"] = True

            if dt_from_iso(framework.get("qualificationPeriod", {}).get("endDate")) < get_request_now():
                LOGGER.info(
                    f"Switched framework {framework['_id']} to complete",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_framework_complete"}),
                )
                framework["status"] = "complete"
                return

    def get_unsuccessful_status_check_date(self, data):
        if period_start := data.get("period", {}).get("startDate"):
            return calculate_framework_full_date(
                dt_from_iso(period_start),
                timedelta(days=self.min_submissions_number_days),
                framework=data,
                working_days=self.min_submissions_number_working_days,
                ceil=True,
            )

    def terminate_agreement(self):
        agreement = self.request.validated.get("agreement")
        if agreement:
            agreement["status"] = "terminated"
            agreement["terminationDetails"] = AGREEMENT_TERMINATION_DETAILS_NOT_ENOUGH_SUBMISSIONS


class AgreementChronographEventsMixing(BaseChronographEventsMixing):
    @staticmethod
    def get_next_check(data):
        checks = []
        if data["status"] == "active":
            milestone_due_dates = [
                milestone["dueDate"]
                for contract in data.get("contracts", [])
                for milestone in contract.get("milestones", [])
                if milestone.get("dueDate") and milestone["status"] == "scheduled"
            ]
            if milestone_due_dates:
                checks.append(min(milestone_due_dates))
            checks.append(data["period"]["endDate"])
        return min(checks) if checks else None

    def on_chronograph_patch(self, data):
        self.check_status(data)
        self.update_next_check(data)

    def check_status(self, data):
        if not self.check_agreement_status(data):
            self.check_contract_statuses(data)

    @staticmethod
    def check_agreement_status(data):
        now = get_request_now()
        if dt_from_iso(data["period"]["endDate"]) < now:
            data["status"] = "terminated"
            return True

    @staticmethod
    def check_contract_statuses(data):
        now = get_request_now()
        for contract in data["contracts"]:
            if contract["status"] == "suspended":
                for milestone in contract["milestones"][::-1]:
                    if milestone["type"] == "ban":
                        if dt_from_iso(milestone["dueDate"]) <= now:
                            contract["status"] = "active"
                            milestone["status"] = "met"
                            milestone["dateModified"] = now.isoformat()
                        break
