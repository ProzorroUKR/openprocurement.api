from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.context import get_tender, get_award
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from openprocurement.api.utils import get_now, raise_operation_error, get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.validation import OPERATIONS


class LimitedReportingContractState(ContractStateMixing, NegotiationTenderState):
    allowed_statuses_from = ("pending",)
    allowed_statuses_to = ("active",)

    def check_contracts_statuses(self, tender: dict) -> None:
        active_contracts = False
        pending_contracts = False

        for contract in tender.get("contracts", []):
            if contract["status"] == "active":
                active_contracts = True
            elif contract["status"] == "pending":
                pending_contracts = True

        if tender.get("contracts", []) and active_contracts and not pending_contracts:
            self.set_object_status(tender, "complete")

    def check_tender_status_method(self) -> None:
        self.check_contracts_statuses(self.request.validated["tender"])

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().contract_on_patch(before, after)

    # validation
    def validate_contract_post(self, request, tender, contract):
        self.validate_contract_operation_not_in_active(request, tender)

    def validate_contract_patch(self, request, before, after):
        tender, award = get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))
        self.validate_contract_operation_not_in_active(request, tender)
        self.validate_contract_update_in_cancelled(request, before)
        # self.validate_update_contract_only_for_active_lots(request, tender, before)
        # self.validate_update_contract_status_by_supplier(request, before, after)
        self.validate_update_contract_status(request, tender, before, after)
        # self.validate_contract_update_with_accepted_complaint(request, tender, before)
        self.validate_update_contract_value(request, before, after)
        self.validate_update_contract_value_net_required(request, before, after)
        self.validate_update_contract_value_with_award(request, before, after)
        self.validate_update_contract_value_amount(request, before, after)
        self.validate_contract_items_count_modification(request, before, after)

    @staticmethod
    def validate_contract_operation_not_in_active(request, tender):
        status = tender["status"]
        if status != "active":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} contract in current "
                f"({status}) tender status"
            )

    @staticmethod
    def validate_contract_update_in_cancelled(request, before):
        if before["status"] == "cancelled":
            raise_operation_error(request, f"Can't update contract in current (cancelled) status")

    @staticmethod
    def validate_contract_items_count_modification(request, before, after):
        # as it is alowed to set/change contract.item.unit.value we need to
        # ensure that nobody is able to add or delete contract.item
        if len(before["items"]) != len(after["items"]):
            raise_operation_error(
                request,
                "Can't change items count"
            )


class LimitedNegotiationContractState(LimitedReportingContractState):

    def check_contracts_lot_statuses(self, tender: dict) -> None:
        now = get_now()
        for lot in tender["lots"]:
            if lot["status"] != "active":
                continue
            lot_awards = [i for i in tender.get("awards", []) if i.get("lotID") == lot["id"]]
            if not lot_awards:
                continue
            last_award = lot_awards[-1]
            pending_awards_complaints = any(
                [i["status"] in ["claim", "answered", "pending"] for a in lot_awards for i in a.get("complaints", [])]
            )
            stand_still_end = max([
                dt_from_iso(award["complaintPeriod"]["endDate"])
                if award.get("complaintPeriod", {}) and award["complaintPeriod"].get("endDate") else now
                for award in lot_awards
            ])
            if pending_awards_complaints or not stand_still_end <= now:
                continue
            elif last_award["status"] == "unsuccessful":
                self.set_object_status(lot, "unsuccessful")
                continue
            elif last_award["status"] == "active" and any(
                    [contract["status"] == "active" and contract.get("awardID") == last_award["id"]
                     for contract in tender.get("contracts")]
            ):
                self.set_object_status(lot, "complete")
        statuses = set([lot["status"] for lot in tender.get("lots", [])])

        if statuses == {"cancelled"}:
            self.set_object_status(tender, "cancelled")
        elif not statuses - {"unsuccessful", "cancelled"}:
            self.set_object_status(tender, "unsuccessful")
        elif not statuses - {"complete", "unsuccessful", "cancelled"}:
            self.set_object_status(tender, "complete")

    def check_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        if tender.get("lots"):
            self.check_contracts_lot_statuses(tender)
        else:
            self.check_contracts_statuses(tender)

    def validate_contract_with_cancellations_and_contract_signing(self) -> None:
        data = self.request.validated["data"]
        tender = self.request.validated["tender"]
        new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19

        if self.request.validated["contract"]["status"] != "active" and "status" in data and data["status"] == "active":
            award_id = self.request.validated["contract"].get("awardID")
            award = [a for a in tender.get("awards")
                     if a["id"] == award_id][0]
            lot_id = award.get("lotID")
            stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("endDate"))
            if stand_still_end > get_now():
                raise_operation_error(
                    self.request,
                    f"Can't sign contract before stand-still period end ({stand_still_end.isoformat()})"
                )

            blocked_complaints = any(
                c["status"] in self.block_complaint_status
                and a.get("lotID") == lot_id
                for a in tender["awards"]
                for c in award.get("complaints", "")
            )

            new_rules_block_complaints = any(
                complaint["status"] in self.block_complaint_status
                and cancellation.get("relatedLot") == lot_id
                for cancellation in tender.get("cancellations", "")
                for complaint in cancellation.get("complaints", "")
            )

            if blocked_complaints or (new_rules and new_rules_block_complaints):
                raise_operation_error(self.request, "Can't sign contract before reviewing all complaints")

    def contract_on_patch(self, before: dict, after: dict):
        tender = get_tender()

        self.validate_contract_with_cancellations_and_contract_signing()
        self.validate_update_contract_only_for_active_lots(self.request, tender, before)
        super().contract_on_patch(before, after)
