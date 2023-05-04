from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from openprocurement.api.utils import raise_operation_error
from datetime import timedelta


class ReportingAwardState(AwardStateMixing, NegotiationTenderState):

    def award_on_patch(self, before, award):
        # start complaintPeriod
        if before["status"] != award["status"]:
            self.award_status_up(before["status"], award["status"], award)
        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before['status']}) status")

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"

        if before == "pending" and after == "active":
            add_contracts(get_request(), award, Contract)
        elif before == "pending" and after == "unsuccessful":
            pass
        elif before == "active" and after == "cancelled":
            self.set_award_contracts_cancelled(award)
        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()


class NegotiationAwardState(ReportingAwardState):
    award_stand_still_time = timedelta(days=10)

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        now = get_now()
        if before == "pending" and after == "active":
            award["complaintPeriod"] = {
                "startDate": now.isoformat(),
                "endDate": calculate_complaint_business_date(now, self.award_stand_still_time, get_tender()).isoformat()
            }
            add_contracts(get_request(), award, Contract)
        elif before == "pending" and after == "unsuccessful":
            award["complaintPeriod"] = {
                "startDate": now.isoformat(),
                "endDate": now.isoformat(),
            }
        elif before == "active" and after == "cancelled":
            if any([i["status"] == "satisfied" for i in award.get("complaints", "")]):
                for i in get_tender().get("awards", ""):
                    if i.get("lotID") == award.get("lotID"):
                        period = i.get("complaintPeriod")
                        if period:
                            if not period.get("endDate") or period["endDate"] > now.isoformat():
                                period["endDate"] = now.isoformat()
                        self.set_object_status(i, "cancelled")
                        self.set_award_contracts_cancelled(i)
            else:
                if award["complaintPeriod"]["endDate"] > now.isoformat():
                    award["complaintPeriod"]["endDate"] = now.isoformat()
                self.set_award_contracts_cancelled(award)
        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()


class NegotiationQuickAwardState(NegotiationAwardState):
    award_stand_still_time = timedelta(days=5)
