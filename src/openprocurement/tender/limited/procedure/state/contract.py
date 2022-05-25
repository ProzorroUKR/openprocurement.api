from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.procedure.state.contract import ContractState
from openprocurement.api.utils import get_now, raise_operation_error, get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19


class LimitedReportingContractState(ContractState):

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

    def on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().on_patch(before, after)


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

            for award in tender.get("awards"):
                if award["id"] == self.request.validated["contract"].get("awardID"):
                    break

            if (
                    tender.get("lots")
                    and tender.get("cancellations")
                    and [
                cancellation
                for cancellation in tender.get("cancellations")
                if (
                        cancellation.get("relatedLot") == award.get("lotID")
                        and cancellation.get("status") not in ["unsuccessful"]
                )
            ]
            ):
                raise_operation_error(self.request, "Can't update contract while cancellation for corresponding lot exists")
            stand_still_end = dt_from_iso(award.get("complaintPeriod", {}).get("endDate"))
            if stand_still_end > get_now():
                raise_operation_error(
                    self.request,
                    "Can't sign contract before stand-still period end ({})".format(stand_still_end.isoformat())
                )

            blocked_complaints = False
            for a in tender["awards"]:
                for complaint in award.get("complaints", []):
                    if (
                            complaint["status"] in self.block_complaint_status and
                            a.lotID == award.lotID
                    ):
                        blocked_complaints = True
                        break
                else:
                    continue
                break

            new_rules_block_complaints = False
            for cancellation in tender.get("cancellations", []):
                for complaint in cancellation.get("complaints", []):
                    if (
                            complaint["status"] in self.block_complaint_status and
                            cancellation.get("relatedLot") == award.get("lotID")
                    ):
                        new_rules_block_complaints = True
                        break
                else:
                    continue
                break
            if blocked_complaints or (new_rules and new_rules_block_complaints):
                raise_operation_error(self.request, "Can't sign contract before reviewing all complaints")

    def on_patch(self, before: dict, after: dict):
        self.validate_contract_with_cancellations_and_contract_signing()
        super().on_patch(before, after)
