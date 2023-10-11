from typing import TYPE_CHECKING

from openprocurement.api.auth import ACCR_3, ACCR_5, ACCR_4
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso, check_auction_period
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState
from openprocurement.tender.openua.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
)
from openprocurement.tender.core.utils import (
    calculate_tender_business_date,
    calculate_clarif_business_date,
)


if TYPE_CHECKING:
    baseclass = OpenUATenderState
else:
    baseclass = object


class OpenUATenderDetailsMixing(TenderDetailsMixing, baseclass):
    period_working_day = False

    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    def initialize_enquiry_period(self, tender):  # openeu, openua
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_tender_business_date(
            tendering_end,
            self.enquiry_period_timedelta,
            tender,
            working_days=self.period_working_day,
        )
        clarifications_until = calculate_clarif_business_date(
            end_date, self.enquiry_stand_still_timedelta, tender, True,
        )
        enquiry_period = tender.get("enquiryPeriod")
        tender["enquiryPeriod"] = dict(
            startDate=tender["tenderPeriod"]["startDate"],
            endDate=end_date.isoformat(),
            clarificationsUntil=clarifications_until.isoformat(),
        )
        invalidation_date = enquiry_period and enquiry_period.get("invalidationDate")
        if invalidation_date:
            tender["enquiryPeriod"]["invalidationDate"] = invalidation_date


class OpenUATenderDetailsState(OpenUATenderDetailsMixing, OpenUATenderState):

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    tendering_period_extra_working_days = False

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)

    def on_patch(self, before, after):
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

        self.validate_tender_exclusion_criteria(before, after)
        self.validate_tender_language_criteria(before, after)

        self.validate_fields_unchanged(before, after)

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.invalidate_bids_data(after)
        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        if after["status"] in ("draft", "active.tendering"):
            self.initialize_enquiry_period(after)

    @staticmethod
    def check_auction_time(tender):
        if check_auction_period(tender.get("auctionPeriod", {}), tender):
            del tender["auctionPeriod"]["startDate"]

        for lot in tender.get("lots", ""):
            if check_auction_period(lot.get("auctionPeriod", {}), tender):
                del lot["auctionPeriod"]["startDate"]
