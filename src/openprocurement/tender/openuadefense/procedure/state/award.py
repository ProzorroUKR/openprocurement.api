from openprocurement.api.constants import (
    NEW_DEFENSE_COMPLAINTS_FROM,
    NEW_DEFENSE_COMPLAINTS_TO,
)
from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.utils import tender_created_in
from openprocurement.tender.openuadefense.constants import STAND_STILL_TIME
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)
from openprocurement.tender.openuadefense.utils import calculate_tender_full_date


class AwardState(AwardStateMixing, OpenUADefenseTenderState):
    contract_model = Contract
    award_stand_still_time = STAND_STILL_TIME

    def award_status_up_from_pending_to_active(self, award, tender):
        end_date = calculate_tender_full_date(
            get_now(),
            STAND_STILL_TIME,
            tender=tender,
            working_days=True,
        ).isoformat()
        award["complaintPeriod"] = {
            "startDate": get_now().isoformat(),
            "endDate": end_date,
        }
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        if new_defence_complaints:
            for i in tender.get("awards"):
                if i.get("lotID") == award.get("lotID") and i.get("status") == "unsuccessful":
                    i["complaintPeriod"] = {
                        "startDate": get_now().isoformat(),
                        "endDate": end_date,
                    }
        self.request.validated["contracts_added"] = add_contracts(self.request, award)
        self.add_next_award()

    def award_status_up_from_active_to_cancelled(self, award, tender):
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        if any(i.get("status") == "satisfied" for i in award.get("complaints", "")):
            for i in tender.get("awards", ""):
                if i.get("lotID") == award.get("lotID"):
                    if self.is_available_to_cancel_award(i, [award["id"]]):
                        self.cancel_award(i, end_complaint_period=not new_defence_complaints)

            self.add_next_award()
        else:
            self.cancel_award(award, end_complaint_period=not new_defence_complaints)
            self.add_next_award()

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)
        if not new_defence_complaints:
            award["complaintPeriod"] = {
                "startDate": get_now().isoformat(),
                "endDate": calculate_tender_full_date(
                    get_now(),
                    self.award_stand_still_time,
                    tender=tender,
                    working_days=True,
                ).isoformat(),
            }
        self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        if not self.has_considered_award_complaints(award, tender):
            raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")

        if tender["status"] == "active.awarded":
            # Go back to active.qualification status
            # because there is no active award anymore
            # for at least one of the lots
            tender["awardPeriod"].pop("endDate", None)
            self.get_change_tender_status_handler("active.qualification")(tender)

        new_defence_complaints = tender_created_in(NEW_DEFENSE_COMPLAINTS_FROM, NEW_DEFENSE_COMPLAINTS_TO)

        for i in tender.get("awards"):
            if i.get("lotID") == award.get("lotID"):
                if self.is_available_to_cancel_award(i, [award["id"]]):
                    self.cancel_award(i, end_complaint_period=not new_defence_complaints)

        self.cancel_award(award, end_complaint_period=not new_defence_complaints)
        self.add_next_award()

    @staticmethod
    def has_considered_award_complaints(current_award, tender):
        considered_statuses = ("satisfied", "resolved")
        for award in tender.get("awards", []):
            if tender.get("lots") and award["lotID"] != current_award["lotID"]:
                continue
            for complaint in award.get("complaints", ""):
                if complaint["status"] in considered_statuses:
                    return True
        return False
