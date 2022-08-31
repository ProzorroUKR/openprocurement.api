from openprocurement.tender.belowthreshold.constants import ENQUIRY_STAND_STILL_TIME
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_clarif_business_date


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)

    def on_patch(self, before, after):
        enquire_start = before.get("enquiryPeriod", {}).get("startDate")
        if enquire_start and not after.get("enquiryPeriod", {}).get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="enquiryPeriod"
            )

        tendering_start = before.get("tenderPeriod", {}).get("startDate")
        if tendering_start and not after.get("tenderPeriod", {}).get("startDate"):
            raise_operation_error(
                get_request(),
                {"startDate": ["This field cannot be deleted"]},
                status=422,
                location="body",
                name="tenderPeriod"
            )

        if after["status"] in ("draft", "active.enquiries"):
            self.initialize_enquiry_period(after)

        super().on_patch(before, after)

    def initialize_enquiry_period(self, tender):
        enquiry_end = dt_from_iso(tender["enquiryPeriod"]["endDate"])
        clarifications_until = calculate_clarif_business_date(
            enquiry_end, self.enquiry_stand_still_timedelta, tender,
        )
        enquiry_period = tender.get("enquiryPeriod")
        tender["enquiryPeriod"]["clarificationsUntil"] = clarifications_until.isoformat()


class TenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
