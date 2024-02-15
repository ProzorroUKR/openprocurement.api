from datetime import timedelta
from typing import TYPE_CHECKING

from openprocurement.api.constants import QUALIFICATION_AFTER_COMPLAINT_FROM
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.contracting import (
    add_contracts,
    save_contracts_to_contracting,
    update_econtracts_statuses,
)
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.utils import calculate_tender_business_date

if TYPE_CHECKING:
    from openprocurement.tender.core.procedure.state.tender import TenderState

    baseclass = TenderState
else:
    baseclass = object


class AwardStateMixing(baseclass):
    contract_model = Contract
    award_stand_still_time: timedelta

    def validate_award_patch(self, before, after):
        request, tender = get_request(), get_tender()
        self.validate_cancellation_blocks(request, tender, lot_id=before.get("lotID"))

    def award_on_patch(self, before, award):
        # start complaintPeriod
        if before["status"] != award["status"]:
            if award["status"] in ("active", "unsuccessful"):
                if not award.get("complaintPeriod"):
                    award["complaintPeriod"] = {}
                award["complaintPeriod"]["startDate"] = get_now().isoformat()

            self.award_status_up(before["status"], award["status"], award)

        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(get_request(), f"Can't update award in current ({before['status']}) status")

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        tender = get_tender()
        awarding_order_enabled = tender["config"]["hasAwardingOrder"]
        now = get_now().isoformat()

        if before == "pending" and after == "active":
            self.award_status_up_from_pending_to_active(award, tender, awarding_order_enabled, working_days=True)

        elif before == "active" and after == "cancelled":
            if award["complaintPeriod"]["endDate"] > now:
                award["complaintPeriod"]["endDate"] = now

            self.set_award_complaints_cancelled(award)
            self.cancel_award(award)
            self.add_next_award()

        elif before == "pending" and after == "unsuccessful":
            self.award_status_up_from_pending_to_unsuccessful(award, tender, working_days=True)

        elif (
            before == "unsuccessful"
            and after == "cancelled"
            and any(i["status"] in ("claim", "answered", "pending", "resolved") for i in award.get("complaints", ""))
        ):
            self.award_status_up_from_unsuccessful_to_cancelled(award, tender, awarding_order_enabled)
        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(), f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = now

    def award_status_up_from_pending_to_active(self, award, tender, awarding_order_enabled, working_days=False):
        if awarding_order_enabled is False:
            self.check_active_awards(award, tender)
        award["complaintPeriod"]["endDate"] = calculate_tender_business_date(
            get_now(), self.award_stand_still_time, tender, working_days
        ).isoformat()
        contracts = add_contracts(get_request(), award)
        self.add_next_award()
        save_contracts_to_contracting(contracts, award)

    def award_status_up_from_pending_to_unsuccessful(self, award, tender, working_days=False):
        award["complaintPeriod"]["endDate"] = calculate_tender_business_date(
            get_now(), self.award_stand_still_time, tender, working_days
        ).isoformat()
        self.add_next_award()

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender, awarding_order_enabled=False):
        now = get_now().isoformat()
        if tender["status"] == "active.awarded":
            self.get_change_tender_status_handler("active.qualification")(tender)
            if "endDate" in tender["awardPeriod"]:
                del tender["awardPeriod"]["endDate"]

        award["complaintPeriod"]["endDate"] = now

        if awarding_order_enabled:
            # If hasAwardingOrder is True, then the current award should be found through all
            # tender awards/lot awards. Then the current award and next ones after it should be cancelled.
            # The new 'pending' award will be generated instead of current one.
            # And qualification will be continued starting from this new award.
            skip = True
            for i in tender.get("awards"):
                # skip all award before the context one
                if i["id"] == award["id"]:
                    skip = False
                if skip:
                    continue
                # skip different lot awards
                if i.get("lotID") != award.get("lotID"):
                    continue
                self.cancel_award_with_complaint_period(i)
        else:
            self.cancel_award_with_complaint_period(award)
        self.add_next_award()

    @staticmethod
    def is_available_to_cancel_award(award, include_awards_ids=None):
        if not include_awards_ids:
            include_awards_ids = []
        is_created_after = tender_created_after(QUALIFICATION_AFTER_COMPLAINT_FROM)
        return (
            is_created_after
            and award["status"] in ("pending", "active")
            or not is_created_after
            or award["id"] in include_awards_ids
        )

    @staticmethod
    def check_active_awards(current_award, tender):
        for award in tender.get("awards", []):
            if (
                award["id"] != current_award["id"]
                and award["status"] == "active"
                and award.get("lotID") == current_award.get("lotID")
            ):
                raise_operation_error(
                    get_request(),
                    f"Can't activate award as tender already has "
                    f"active award{' for this lot' if current_award.get('lotID') else ''}",
                    status=422,
                    name="awards",
                )

    def cancel_award_with_complaint_period(self, award):
        now = get_now().isoformat()
        # update complaintPeriod.endDate if there is a need
        if award.get("complaintPeriod") and (
            not award["complaintPeriod"].get("endDate") or award["complaintPeriod"]["endDate"] > now
        ):
            award["complaintPeriod"]["endDate"] = now

        self.set_award_complaints_cancelled(award)
        self.cancel_award(award)

    def cancel_award(self, award):
        self.set_object_status(award, "cancelled")
        contracts_ids = self.set_award_contracts_cancelled(award)
        update_econtracts_statuses(contracts_ids, "cancelled")

    # helpers
    @classmethod
    def set_award_contracts_cancelled(cls, award):
        tender = get_tender()
        cancelled_contracts_ids = []
        for contract in tender.get("contracts", tuple()):
            if contract["awardID"] == award["id"]:
                if contract["status"] != "active":
                    cls.set_object_status(contract, "cancelled")
                    cancelled_contracts_ids.append(contract["id"])
                else:
                    raise_operation_error(get_request(), "Can't cancel award contract in active status")
        return cancelled_contracts_ids

    @classmethod
    def set_award_complaints_cancelled(cls, award):
        for complaint in award.get("complaints", ""):
            if complaint["status"] not in ("invalid", "resolved", "declined"):
                cls.set_object_status(complaint, "cancelled")
                complaint["cancellationReason"] = "cancelled"
                complaint["dateCanceled"] = get_now().isoformat()


# example use
class AwardState(AwardStateMixing, TenderState):
    pass
