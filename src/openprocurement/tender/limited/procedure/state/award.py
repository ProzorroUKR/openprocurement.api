from datetime import timedelta

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class ReportingAwardState(AwardStateMixing, NegotiationTenderState):
    contract_model = Contract

    def award_status_up_from_pending_to_active(self, award, tender):
        self.request.validated["contracts_added"] = add_contracts(self.request, award)

    def award_status_up_from_active_to_cancelled(self, award, tender):
        self.cancel_award(award)

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        pass

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        raise_operation_error(self.request, f"Can't update award in current (unsuccessful) status")


class NegotiationAwardState(ReportingAwardState):
    contract_model = Contract
    award_stand_still_time = timedelta(days=10)

    def award_status_up_from_pending_to_active(self, award, tender):
        award["complaintPeriod"] = {
            "startDate": get_now().isoformat(),
            "endDate": calculate_complaint_business_date(
                get_now(),
                self.award_stand_still_time,
                get_tender(),
            ).isoformat(),
        }
        self.request.validated["contracts_added"] = add_contracts(self.request, award)

    def award_status_up_from_active_to_cancelled(self, award, tender):
        if any(i["status"] == "satisfied" for i in award.get("complaints", "")):
            for i in get_tender().get("awards", ""):
                if i.get("lotID") == award.get("lotID"):
                    self.cancel_award(i)
        else:
            self.cancel_award(award)

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
        award["complaintPeriod"] = {
            "startDate": get_now().isoformat(),
            "endDate": get_now().isoformat(),
        }

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        raise_operation_error(self.request, f"Can't update award in current (unsuccessful) status")


class NegotiationQuickAwardState(NegotiationAwardState):
    award_stand_still_time = timedelta(days=5)
