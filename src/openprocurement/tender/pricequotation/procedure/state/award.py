from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.api.utils import raise_operation_error


class AwardState(AwardStateMixing, PriceQuotationTenderState):

    @staticmethod
    def tender_is_awarded(award):
        is_awarded = any(
            a["bid_id"] == award["bid_id"] and a["id"] != award["id"]
            for a in get_tender().get("awards", [])
        )
        return is_awarded

    def award_on_patch(self, before, award):
        if self.tender_is_awarded(award) and award["status"] not in ('unsuccessful', 'pending'):
            raise_operation_error(
                self.request,
                "Can't change award status to {} from {}".format(award["status"], before["status"])
            )
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
            self.add_next_award()

        elif before == "pending" and after == "unsuccessful":
            if self.tender_is_awarded(award):
                handler = self.get_change_tender_status_handler("unsuccessful")
                handler(get_tender())
            else:
                self.add_next_award()

        elif before == "active" and after == "cancelled":
            self.set_award_contracts_cancelled(award)
            self.add_next_award()
        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before}) status")
        # date updated when status updated
        award["date"] = get_now().isoformat()

