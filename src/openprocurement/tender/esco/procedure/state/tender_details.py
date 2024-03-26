from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.esco.constants import (
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_STAND_STILL_TIME,
    QUESTIONS_STAND_STILL,
)
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState as BaseTenderDetailsState,
)


class ESCOTenderDetailsState(BaseTenderDetailsState):
    enquiry_period_timedelta = -QUESTIONS_STAND_STILL
    enquiry_stand_still_timedelta = ENQUIRY_STAND_STILL_TIME
    should_validate_notice_doc_required = False

    required_criteria = {
        "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
        "CRITERION.EXCLUSION.CONVICTIONS.FRAUD",
        "CRITERION.EXCLUSION.CONVICTIONS.CORRUPTION",
        "CRITERION.EXCLUSION.CONVICTIONS.CHILD_LABOUR-HUMAN_TRAFFICKING",
        "CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES",
        "CRITERION.EXCLUSION.BUSINESS.BANKRUPTCY",
        "CRITERION.EXCLUSION.MISCONDUCT.MARKET_DISTORTION",
        "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.MISINTERPRETATION",
        "CRITERION.EXCLUSION.NATIONAL.OTHER",
        "CRITERION.OTHER.BID.LANGUAGE",
    }

    def on_post(self, tender):
        super().on_post(tender)
        self.update_periods(tender)

    def on_patch(self, before, after):
        super().on_patch(before, after)
        self.validate_related_lot_in_items(after)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        self.update_periods(data)

    @staticmethod
    def watch_value_meta_changes(tender):
        pass

    @staticmethod
    def update_periods(tender):
        tendering_end = dt_from_iso(tender["tenderPeriod"]["endDate"])
        end_date = calculate_complaint_business_date(tendering_end, -COMPLAINT_SUBMIT_TIME, tender)
        tender["complaintPeriod"] = dict(
            startDate=tender["tenderPeriod"]["startDate"],
            endDate=end_date.isoformat(),
        )

        if tender["status"] == "active.tendering" and not tender.get("noticePublicationDate"):
            tender["noticePublicationDate"] = get_now().isoformat()

    def validate_minimal_step(self, data, before=None):
        # TODO: adjust this validation in case of it will be allowed to disable auction in esco
        # TODO: Look at original validate_minimal_step in openprocurement.tender.core.procedure.state.tender
        minimal_step_fields = ("minimalStepPercentage", "yearlyPaymentsPercentageRange")
        for field in minimal_step_fields:
            if data.get(field) is None:
                raise_operation_error(
                    self.request,
                    ["This field is required."],
                    status=422,
                    location="body",
                    name=field,
                )
