from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.cfaua.constants import MIN_BIDS_NUMBER
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS


class AgreementStateMixing:
    block_complaint_status: tuple  # from TenderState

    def agreement_on_patch(self, before, after):
        if before["status"] != after["status"]:
            self.agreement_status_up(before["status"], after["status"], after)

    def agreement_status_up(self, before, after, agreement):
        request = get_request()
        if before != "pending" or after not in ("active", "unsuccessful"):
            raise_operation_error(request, "Can't update agreement status")

        if after == "active":
            tender = get_tender()

            award_ids = {c["awardID"] for c in agreement.get("contracts", [])}
            lot_ids = {award["lotID"] for award in tender.get("awards", [])
                       if award["id"] in award_ids}
            lot_ids.add(None)

            pending_complaints = (
                i["status"] in self.block_complaint_status
                for i in tender.get("complaints", [])
                if i.get("relatedLot") in lot_ids
            )
            pending_awards_complaints = (
                i["status"] in self.block_complaint_status
                for a in tender.get("awards", "")
                for i in a.get("complaints", "")
                if a.get("lotID") in lot_ids
            )
            if any(pending_complaints) or any(pending_awards_complaints):
                raise_operation_error(request, "Can't sign agreement before reviewing all complaints")

            if any(
                unit_price.get("value", {}).get("amount") is None
                for contract in agreement.get("contracts", "")
                if contract["status"] == "active"
                for unit_price in contract.get("unitPrices", "")
            ):
                raise_operation_error(request, "Can't sign agreement without all contracts.unitPrices.value.amount",
                                      status=422)

            if sum(1 for c in agreement.get("contracts", "") if c["status"] == "active") < MIN_BIDS_NUMBER:
                raise_operation_error(request, "Agreement don't reach minimum active contracts.", status=422)

            if not agreement.get("dateSigned"):
                agreement["dateSigned"] = get_now().isoformat()

            # success
            clarifications_until = tender["contractPeriod"]["clarificationsUntil"]
            if dt_from_iso(agreement["dateSigned"]) < dt_from_iso(clarifications_until):
                raise_operation_error(
                    get_request(),
                    "Agreement signature date should be after "
                    f"contractPeriod.clarificationsUntil ({clarifications_until})",
                    status=422,
                )

    # Validators
    def validate_agreement_on_patch(self, before, _):
        request, tender = get_request(), get_tender()
        self.validate_agreement_in_allowed_tender_status(request, tender)
        self.validate_update_agreement_only_for_active_lots(request, tender, before)
        self.validate_agreement_update_with_accepted_complaint(request, tender, before)

    @staticmethod
    def validate_agreement_in_allowed_tender_status(request, tender):
        if tender['status'] != "active.awarded":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} agreement in current ({tender['status']}) tender status",
            )

    @staticmethod
    def validate_update_agreement_only_for_active_lots(request, tender, agreement):
        award_ids = {c["awardID"] for c in agreement.get("contracts", "")}
        lot_ids = {award["lotID"] for award in tender.get("awards", "")
                   if award["id"] in award_ids}
        if any(
            lot["status"] != "active"
            for lot in tender.get("lots", "")
            if lot["id"] in lot_ids
        ):
            raise_operation_error(request, "Can update agreement only in active lot status")

    @staticmethod
    def validate_agreement_update_with_accepted_complaint(request, tender, agreement):
        award_ids = {c["awardID"] for c in agreement.get("contracts", "")}
        lot_ids = {award["lotID"] for award in tender.get("awards", "")
                   if award["id"] in award_ids}
        if any(
            any(c["status"] == "accepted" for c in award.get("complaints", ""))
            for award in tender.get("awards", "")
            if award["lotID"] in lot_ids
        ):
            raise_operation_error(request, "Can't update agreement with accepted complaint")


class AgreementState(AgreementStateMixing, CFAUATenderState):
    def agreement_on_patch(self, before, after):
        super().agreement_on_patch(before, after)
        self.check_tender_status_on_active_awarded()

    def check_tender_status_on_active_awarded(self):
        tender = get_tender()
        statuses = {agreement["status"] for agreement in tender.get("agreements")}
        if statuses == {"cancelled"}:
            self.get_change_tender_status_handler("cancelled")(tender)

        elif not statuses.difference({"unsuccessful", "cancelled"}):
            self.get_change_tender_status_handler("unsuccessful")(tender)

        elif not statuses.difference({"active", "unsuccessful", "cancelled"}):
            self.get_change_tender_status_handler("complete")(tender)
            tender["contractPeriod"]["endDate"] = get_now().isoformat()
