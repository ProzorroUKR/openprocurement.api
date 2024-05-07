from datetime import timedelta

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class ReportingAwardState(AwardStateMixing, NegotiationTenderState):
    contract_model = Contract

    def award_on_patch(self, before, award):
        # start complaintPeriod
        if before["status"] != award["status"]:
            self.award_status_up(before["status"], award["status"], award)
        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(get_request(), f"Can't update award in current ({before['status']}) status")

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        request = get_request()
        if before == "pending" and after == "active":
            request.validated["contracts_added"] = add_contracts(request, award)
        elif before == "pending" and after == "unsuccessful":
            pass
        elif before == "active" and after == "cancelled":
            self.cancel_award(award)
        else:  # any other state transitions are forbidden
            raise_operation_error(request, f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()


class NegotiationAwardState(ReportingAwardState):
    contract_model = Contract

    def award_status_up(self, before, after, award):
        tender = get_tender()
        award_complain_duration = tender["config"]["awardComplainDuration"]
        assert before != after, "Statuses must be different"
        now = get_now()
        if before == "pending" and after == "active":
            if award_complain_duration > 0:
                award["complaintPeriod"] = {
                    "startDate": now.isoformat(),
                    "endDate": calculate_complaint_business_date(
                        now, timedelta(days=award_complain_duration), get_tender()
                    ).isoformat(),
                }
            self.request.validated["contracts_added"] = add_contracts(get_request(), award)
        elif before == "pending" and after == "unsuccessful":
            award["complaintPeriod"] = {
                "startDate": now.isoformat(),
                "endDate": now.isoformat(),
            }
        elif before == "active" and after == "cancelled":
            if any(i["status"] == "satisfied" for i in award.get("complaints", "")):
                for i in get_tender().get("awards", ""):
                    if i.get("lotID") == award.get("lotID"):
                        period = i.get("complaintPeriod")
                        if period:
                            if not period.get("endDate") or period["endDate"] > now.isoformat():
                                period["endDate"] = now.isoformat()
                        self.cancel_award(i)
            else:
                if award["complaintPeriod"]["endDate"] > now.isoformat():
                    award["complaintPeriod"]["endDate"] = now.isoformat()
                self.cancel_award(award)
        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(), f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()


class NegotiationQuickAwardState(NegotiationAwardState):
    pass
