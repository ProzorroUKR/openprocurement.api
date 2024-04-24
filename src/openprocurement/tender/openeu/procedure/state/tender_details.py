from openprocurement.api.auth import ACCR_3, ACCR_4, ACCR_5
from openprocurement.api.context import get_now
from openprocurement.tender.openeu.constants import (
    PREQUALIFICATION_COMPLAINT_STAND_STILL,
)
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.constants import (
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_PERIOD_TIME,
    ENQUIRY_STAND_STILL_TIME,
    TENDERING_EXTRA_PERIOD,
)
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsMixing,
)


class OpenEUTenderDetailsMixing(OpenUATenderDetailsMixing):
    tender_create_accreditations = (ACCR_3, ACCR_5)
    tender_central_accreditations = (ACCR_5,)
    tender_edit_accreditations = (ACCR_4,)

    required_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
        "CRITERION.OTHER.BID.LANGUAGE",
    }

    tendering_period_extra = TENDERING_EXTRA_PERIOD
    complaint_submit_time = COMPLAINT_SUBMIT_TIME

    enquiry_period_timedelta = -ENQUIRY_PERIOD_TIME
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
    pre_qualification_complaint_stand_still = PREQUALIFICATION_COMPLAINT_STAND_STILL

    def on_post(self, tender):
        super().on_post(tender)  # TenderDetailsMixing.on_post
        self.initialize_enquiry_period(tender)

    def on_patch(self, before, after):
        self.validate_items_classification_prefix_unchanged(before, after)

        # bid invalidation rules
        if before["status"] == "active.tendering":
            self.validate_tender_period_extension(after)
            self.invalidate_bids_data(after)

        elif after["status"] == "active.tendering":
            after["enquiryPeriod"]["invalidationDate"] = get_now().isoformat()

        if after["status"] in ("draft", "draft.stage2", "active.tendering"):
            self.initialize_enquiry_period(after)

        super().on_patch(before, after)  # TenderDetailsMixing.on_patch
        self.validate_related_lot_in_items(after)


class OpenEUTenderDetailsState(OpenEUTenderDetailsMixing, BaseOpenEUTenderState):
    pass
