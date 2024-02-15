from datetime import timedelta
from logging import getLogger

from openprocurement.api.context import get_now, get_request
from openprocurement.api.utils import context_unpack
from openprocurement.framework.core.constants import DAYS_TO_UNSUCCESSFUL_STATUS
from openprocurement.framework.core.procedure.utils import (
    get_framework_number_of_submissions,
)
from openprocurement.framework.core.utils import calculate_framework_date
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class ChronographEventsMixing:
    def update_next_check(self, data):
        # next_check is field that shows object's expectation to be triggered at a certain time
        next_check = self.get_next_check(data)
        if next_check is not None:
            data["next_check"] = next_check
        elif "next_check" in data:
            del data["next_check"]

    def get_next_check(self, data):
        pass

    def check_status(self, framework):
        if framework.get("status") == "active":
            if not framework.get("successful"):
                if start_date := framework.get("period", {}).get("startDate"):
                    unsuccessful_status_check = calculate_framework_date(
                        dt_from_iso(start_date),
                        timedelta(days=DAYS_TO_UNSUCCESSFUL_STATUS),
                        framework,
                        working_days=True,
                        ceil=True,
                    )
                    if unsuccessful_status_check < get_now():
                        number_of_submissions = get_framework_number_of_submissions(get_request(), framework)
                        if number_of_submissions == 0:
                            LOGGER.info(
                                f"Switched framework {framework['_id']} to unsuccessful",
                                extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_framework_unsuccessful"}),
                            )
                            framework["status"] = "unsuccessful"
                            return
                        else:
                            framework["successful"] = True

            if dt_from_iso(framework.get("qualificationPeriod", {}).get("endDate")) < get_now():
                LOGGER.info(
                    f"Switched framework {framework['_id']} to complete",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "switched_framework_complete"}),
                )
                framework["status"] = "complete"
                return

    def patch_statuses_by_chronograph(self, data):
        if not self.check_agreement_status(data):
            self.check_contract_statuses(data)
        self.update_next_check(data)

    @staticmethod
    def check_agreement_status(data):
        now = get_now()
        if dt_from_iso(data["period"]["endDate"]) < now:
            data["status"] = "terminated"
            for contract in data["contracts"]:
                for milestone in contract["milestones"]:
                    if milestone.get("status", "scheduled") == "scheduled":
                        milestone["status"] = (
                            "met" if milestone.get("dueDate") and dt_from_iso(milestone["dueDate"]) <= now else "notMet"
                        )
                        milestone["dateModified"] = now

                if contract["status"] == "active":
                    contract["status"] = "terminated"
            return True

    @staticmethod
    def check_contract_statuses(data):
        now = get_now()
        for contract in data["contracts"]:
            if contract["status"] == "suspended":
                for milestone in contract["milestones"][::-1]:
                    if milestone["type"] == "ban":
                        if dt_from_iso(milestone["dueDate"]) <= now:
                            contract["status"] = "active"
                            milestone["status"] = "met"
                            milestone["dateModified"] = now.isoformat()
                        break
