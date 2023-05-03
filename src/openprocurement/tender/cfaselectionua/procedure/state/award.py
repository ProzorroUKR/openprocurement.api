from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.api.utils import raise_operation_error, context_unpack
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.cfaselectionua.constants import STAND_STILL_TIME
import logging

LOGGER = logging.getLogger(__name__)


class AwardState(AwardStateMixing, CFASelectionTenderState):
    award_stand_still_time = STAND_STILL_TIME

    def award_on_patch(self, before, award):
        if before["status"] != award["status"]:
            self.award_status_up(before["status"], award["status"], award)

        elif award["status"] == "pending":
            pass  # allowing to update award in pending status
        else:
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before['status']}) status")

    def award_status_up(self, before, after, award):
        assert before != after, "Statuses must be different"
        tender = get_tender()

        if before == "pending" and after == "active":
            add_contracts(get_request(), award, Contract)
            self.add_next_award()

        elif before == "active" and after == "cancelled":
            self.set_award_contracts_cancelled(award)
            self.add_next_award()

        elif before == "pending" and after == "unsuccessful":
            if tender["status"] == "active.qualification":
                if not any(
                    a["bid_id"] == award["bid_id"]
                    and a["status"] == "cancelled"  # not need to check `a["id"] != award["id"]`
                    for a in tender.get("awards", [])
                ):
                    raise_operation_error(
                        self.request,
                        f"Can't update award status to {award['status']}, if tender status is {tender['status']}"
                        " and there is no cancelled award with the same bid_id",
                    )
            self.add_next_award()
        else:  # any other state transitions are forbidden
            raise_operation_error(get_request(),
                                  f"Can't update award in current ({before}) status")

        # code from openprocurement.tender.cfaselectionua.utils.check_tender_status
        # TODO: find a better place ?
        lots = tender.get("lots")
        if lots:
            for lot in lots:
                if lot["status"] == "active":
                    lot_awards = [i for i in tender.get("awards", []) if i["lotID"] == lot["id"]]
                    if lot_awards:
                        last_award = lot_awards[-1]
                        if last_award["status"] == "unsuccessful":
                            LOGGER.info(
                                f"Switched lot {lot['id']} of tender {tender['_id']} to unsuccessful",
                                extra=context_unpack(get_request(),
                                                     {"MESSAGE_ID": "switched_lot_unsuccessful"},
                                                     {"LOT_ID": lot["id"]}),
                            )
                            self.set_object_status(lot, "unsuccessful")

                        elif last_award["status"] == "active":
                            contract_statuses = {
                                contract["status"]
                                for contract in tender.get("contracts", [])
                                if contract["awardID"] == last_award["id"]
                            }
                            if (
                                contract_statuses
                                and "active" in contract_statuses
                                and "pending" not in contract_statuses
                            ):
                                LOGGER.info(
                                    f"Switched lot {lot['id']} of tender {tender['_id']} to complete",
                                    extra=context_unpack(get_request(),
                                                         {"MESSAGE_ID": "switched_lot_complete"},
                                                         {"LOT_ID": lot["id"]}),
                                )
                                self.set_object_status(lot, "complete")

            statuses = {lot.get("status") for lot in tender.get("lots", [])}
            if statuses == {"cancelled"}:
                self.get_change_tender_status_handler("cancelled")(tender)

            elif not statuses.difference({"unsuccessful", "cancelled"}):
                self.get_change_tender_status_handler("unsuccessful")(tender)

            elif not statuses.difference({"complete", "unsuccessful", "cancelled"}):
                self.get_change_tender_status_handler("complete")(tender)

        else:
            awards = tender.get("awards")
            if awards:
                last_award_status = awards[-1]["status"]
                if last_award_status == "unsuccessful":
                    self.get_change_tender_status_handler("unsuccessful")(tender)

            contract_statuses = {c["status"] for c in tender.get("contracts", [])}
            if (
                contract_statuses
                and "active" in contract_statuses
                and "pending"not in contract_statuses
            ):
                self.get_change_tender_status_handler("complete")(tender)

        # date updated when status updated
        award["date"] = get_now().isoformat()
