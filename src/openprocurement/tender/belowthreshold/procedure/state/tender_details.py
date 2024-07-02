from datetime import timedelta

from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_5
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.belowthreshold.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.belowthreshold.procedure.models.tender import (
    PatchActiveTender,
    PatchDraftTender,
    PatchTender,
)
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixing,
)
from openprocurement.tender.core.procedure.utils import (
    check_auction_period,
    dt_from_iso,
)
from openprocurement.tender.core.utils import calculate_clarif_business_date


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
    tender_create_accreditations = (ACCR_1, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_2,)

    tendering_period_extra_working_days = True
    tendering_period_extra = TENDERING_EXTRA_PERIOD
    should_validate_notice_doc_required = True

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post

    def on_patch(self, before, after):
        enquire_start = before.get("enquiryPeriod", {}).get("startDate")
        if enquire_start and not after.get("enquiryPeriod", {}).get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="enquiryPeriod",
            )

        tendering_start = before.get("tenderPeriod", {}).get("startDate")
        if tendering_start and not after.get("tenderPeriod", {}).get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="tenderPeriod",
            )

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        super().on_patch(before, after)
        self.validate_related_lot_in_items(after)

    def invalidate_bids_data(self, tender):
        self.check_auction_time(tender)
        tender["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()
        for bid in tender.get("bids", ""):
            if bid.get("status") not in ("deleted", "draft"):
                bid["status"] = "invalid"

    @staticmethod
    def check_auction_time(tender):
        if check_auction_period(tender.get("auctionPeriod", {}), tender):
            del tender["auctionPeriod"]["startDate"]

        for lot in tender.get("lots", ""):
            if check_auction_period(lot.get("auctionPeriod", {}), tender):
                del lot["auctionPeriod"]["startDate"]

    def initialize_enquiry_period(self, tender):
        clarification_until_duration = tender["config"]["clarificationUntilDuration"]
        enquiry_end = dt_from_iso(tender["enquiryPeriod"]["endDate"])
        clarifications_until = calculate_clarif_business_date(
            enquiry_end,
            timedelta(days=clarification_until_duration),
            tender,
            self.clarification_period_working_day,
        )
        tender["enquiryPeriod"]["clarificationsUntil"] = clarifications_until.isoformat()

    def get_patch_data_model(self):
        tender = get_tender()
        if tender.get("status", "") == "active.tendering":
            return PatchActiveTender
        elif tender.get("status", "") in ("draft", "active.enquiries"):
            return PatchDraftTender
        return PatchTender


class BelowThresholdTenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    pass
