import logging

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import context_unpack, raise_operation_error
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.contracting import add_contracts
from openprocurement.tender.core.procedure.models.contract import Contract
from openprocurement.tender.core.procedure.state.award import AwardStateMixing

LOGGER = logging.getLogger(__name__)


class AwardState(AwardStateMixing, CFASelectionTenderState):
    contract_model = Contract
    generate_award_milestones = False

    def award_status_up(self, before, after, award):
        super().award_status_up(before, after, award)

        # code from openprocurement.tender.cfaselectionua.utils.check_tender_status
        # TODO: find a better place ?
        tender = get_tender()
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
                                extra=context_unpack(
                                    self.request,
                                    {"MESSAGE_ID": "switched_lot_unsuccessful"},
                                    {"LOT_ID": lot["id"]},
                                ),
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
                                    extra=context_unpack(
                                        self.request,
                                        {"MESSAGE_ID": "switched_lot_complete"},
                                        {"LOT_ID": lot["id"]},
                                    ),
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
            if contract_statuses and "active" in contract_statuses and "pending" not in contract_statuses:
                self.get_change_tender_status_handler("complete")(tender)

    def award_status_up_from_pending_to_active(self, award, tender):
        self.request.validated["contracts_added"] = add_contracts(self.request, award)
        self.add_next_award()

    def award_status_up_from_active_to_cancelled(self, award, tender):
        self.cancel_award(award)
        self.add_next_award()

    def award_status_up_from_pending_to_unsuccessful(self, award, tender):
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

    def award_status_up_from_unsuccessful_to_cancelled(self, award, tender):
        raise_operation_error(self.request, "Can't update award in current (unsuccessful) status")
