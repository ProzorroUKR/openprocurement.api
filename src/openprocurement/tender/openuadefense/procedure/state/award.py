from openprocurement.api.constants import (
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.utils import tender_created_in
from openprocurement.tender.openuadefense.constants import STAND_STILL_TIME
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)
from openprocurement.tender.openuadefense.utils import calculate_complaint_business_date


class AwardState(AwardStateMixing, OpenUADefenseTenderState):
    contract_model = Contract
    award_stand_still_time = STAND_STILL_TIME

    def award_on_patch(self, before, award):
        # start complaintPeriod
        if before["status"] != award["status"]:
            # if award["status"] in ("active", "unsuccessful"):
            #     if not award.get("complaintPeriod"):
            #         award["complaintPeriod"] = {}
            #     award["complaintPeriod"]["startDate"] = get_now().isoformat()

            self.award_status_up(before["status"], award["status"], award)

        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(get_request(), f"Can't update award in current ({before['status']}) status")

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"

        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)

        tender = get_tender()
        now = get_now().isoformat()

        if before == "pending" and after == "active":
            end_date = calculate_complaint_business_date(get_now(), STAND_STILL_TIME, tender, True).isoformat()
            award["complaintPeriod"] = {
                "startDate": now,
                "endDate": end_date,
            }
            if new_defence_complaints:
                for i in tender.get("awards"):
                    if i.get("lotID") == award.get("lotID") and i.get("status") == "unsuccessful":
                        i["complaintPeriod"] = {
                            "startDate": now,
                            "endDate": end_date,
                        }
            self.request.validated["contracts_added"] = add_contracts(get_request(), award)
            self.add_next_award()

        elif before == "pending" and after == "unsuccessful":
            if not new_defence_complaints:
                award["complaintPeriod"] = {
                    "startDate": now,
                    "endDate": calculate_complaint_business_date(
                        get_now(), self.award_stand_still_time, tender, True
                    ).isoformat(),
                }
            self.add_next_award()

        elif before == "active" and after == "cancelled":
            if any(i.get("status") == "satisfied" for i in award.get("complaints", "")):
                for i in tender.get("awards", ""):
                    if i.get("lotID") == award.get("lotID"):
                        if self.is_available_to_cancel_award(i, [award["id"]]):
                            self.cancel_award(i)

                self.add_next_award()
            else:
                self.cancel_award(award)
                self.add_next_award()
        elif before == "unsuccessful" and after == "cancelled" and self.has_considered_award_complaints(award, tender):
            if tender["status"] == "active.awarded":
                self.set_object_status(tender, "active.qualification")
                if "endDate" in tender["awardPeriod"]:
                    del tender["awardPeriod"]["endDate"]

            if not new_defence_complaints and award["complaintPeriod"]["endDate"] > now:
                award["complaintPeriod"]["endDate"] = now

            for i in tender.get("awards"):
                if i.get("lotID") == award.get("lotID"):
                    if self.is_available_to_cancel_award(i, [award["id"]]):
                        self.cancel_award(i)
            self.add_next_award()

        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(), f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()
