from logging import getLogger

from openprocurement.api.constants_env import NO_DEFENSE_AWARD_CLAIMS_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date, raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class AwardClaimStateMixin(ClaimStateMixin):
    create_allowed_tender_statuses = ("active.qualification", "active.awarded")
    update_allowed_tender_statuses = ("active.qualification", "active.awarded")
    patch_as_complaint_owner_tender_statuses = (
        "active.qualification",
        "active.awarded",
    )
    # openuadefense: award claims are not accepted for tenders created after NO_DEFENSE_AWARD_CLAIMS_FROM
    award_claims_forbidden_by_date = False

    def validate_claim_on_post(self, complaint):
        if self.award_claims_forbidden_by_date:
            tender = get_tender()
            tender_created = get_first_revision_date(tender, default=get_request_now())
            if tender_created > NO_DEFENSE_AWARD_CLAIMS_FROM:
                raise_operation_error(self.request, "Can't add complaint of 'claim' type")
        super().validate_claim_on_post(complaint)

    def claim_on_post(self, complaint):
        request = self.request
        if lot_id := request.validated["award"].get("lotID"):
            complaint["relatedLot"] = lot_id
        super().claim_on_post(complaint)

    def validate_tender_in_complaint_period(self, tender):
        award = get_award()
        period = award.get("complaintPeriod")
        if award.get("status") in ("active", "unsuccessful") and period:
            if dt_from_iso(period.get("startDate")) <= get_request_now() < dt_from_iso(period.get("endDate")):
                return
        operation = OPERATIONS.get(self.request.method)
        raise_operation_error(self.request, f"Can {operation} complaint only in complaintPeriod")

    def validate_submit_claim(self, claim):
        if not self.claim_submit_validation:
            return
        award = get_award()
        if award.get("status") == "unsuccessful" and award.get("bid_id") != claim.get("bid_id"):
            raise_operation_error(self.request, "Can add claim only on unsuccessful award of your bid")
        if award.get("status") == "pending":
            raise_operation_error(self.request, "Claim submission is not allowed on pending award")

    def validate_tender_owner_update_claim_time(self):
        pass

    def validate_lot_status(self):
        tender = get_tender()
        award = get_award()
        lot_id = award.get("lotID")
        if lot_id and any(
            lot.get("status") != "active" for lot in tender.get("lots", []) if lot["id"] == award.get("lotID")
        ):
            operation = OPERATIONS.get(self.request.method)
            raise_operation_error(self.request, f"Can {operation} complaint only in active lot status")


class AwardClaimState(AwardClaimStateMixin, TenderState):
    pass
