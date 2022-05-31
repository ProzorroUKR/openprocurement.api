from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState
from openprocurement.api.utils import get_now, raise_operation_error, get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19


class LimitedReportingContractState(ContractStateMixing, NegotiationTenderState):

    @staticmethod
    def check_contracts_statuses(tender: dict) -> None:
        active_contracts = False
        pending_contracts = False

        for contract in tender.get("contracts", []):
            if contract["status"] == "active":
                active_contracts = True
            elif contract["status"] == "pending":
                pending_contracts = True

        if tender.get("contracts", []) and active_contracts and not pending_contracts:
            tender["status"] = "complete"

    def check_tender_status_method(self) -> None:
        self.check_contracts_statuses(self.request.validated["tender"])

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().contract_on_patch(before, after)


class LimitedNegotiationContractState(LimitedReportingContractState):

    @staticmethod
    def check_contracts_lot_statuses(tender: dict) -> None:
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
                lot["status"] = "unsuccessful"
                continue
            elif last_award["status"] == "active" and any(
                    [contract["status"] == "active" and contract.get("awardID") == last_award["id"]
                     for contract in tender.get("contracts")]
            ):
                lot["status"] = "complete"
        statuses = set([lot["status"] for lot in tender.get("lots", [])])

        if statuses == {"cancelled"}:
            tender["status"] = "cancelled"
        elif not statuses - {"unsuccessful", "cancelled"}:
            tender["status"] = "unsuccessful"
        elif not statuses - {"complete", "unsuccessful", "cancelled"}:
            tender["status"] = "complete"

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

            if (
                tender.get("lots")
                and any(
                    cancellation.get("relatedLot") == lot_id
                    and cancellation.get("status") != "unsuccessful"
                    for cancellation in tender.get("cancellations", "")
                )
            ):
                raise_operation_error(self.request,
                                      "Can't update contract while cancellation for corresponding lot exists")
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
        self.validate_contract_with_cancellations_and_contract_signing()
        super().contract_on_patch(before, after)
