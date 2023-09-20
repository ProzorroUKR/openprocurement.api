from typing import TYPE_CHECKING

from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.openeu.constants import PREQUALIFICATION_COMPLAINT_STAND_STILL
from openprocurement.tender.openua.constants import (
    TENDERING_EXTRA_PERIOD,
    ENQUIRY_PERIOD_TIME,
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_STAND_STILL_TIME,
)
from openprocurement.tender.openua.procedure.state.tender_details import OpenUATenderDetailsMixing


if TYPE_CHECKING:
    baseclass = BaseOpenEUTenderState
else:
    baseclass = object


class OpenEUTenderDetailsMixing(OpenUATenderDetailsMixing, baseclass):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    tendering_period_extra = TENDERING_EXTRA_PERIOD

    enquiry_period_timedelta = - ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
    pre_qualification_complaint_stand_still = PREQUALIFICATION_COMPLAINT_STAND_STILL

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)
        self.update_complaint_period(tender)

    def on_patch(self, before, after):
        self.validate_fields_unchanged(before, after)

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.update_complaint_period(after)
            self.invalidate_bids_data(after)

        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        if after["status"] in ("draft", "draft.stage2", "active.tendering"):
            self.initialize_enquiry_period(after)

        self.validate_tender_exclusion_criteria(before, after)
        self.validate_tender_language_criteria(before, after)
        super().on_patch(before, after)  # TenderDetailsMixing.on_patch

    @staticmethod
    def update_complaint_period(tender):
        if "tenderPeriod" in tender and "endDate" in tender["tenderPeriod"]:
            tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
            end_date = calculate_complaint_business_date(tendering_end, -COMPLAINT_SUBMIT_TIME, tender).isoformat()
            tender["complaintPeriod"] = dict(startDate=tender["tenderPeriod"]["startDate"], endDate=end_date)


class OpenEUTenderDetailsState(OpenEUTenderDetailsMixing, BaseOpenEUTenderState):
    pass
