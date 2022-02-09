from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixing
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.api.utils import raise_operation_error


class BelowThresholdTenderDetailsMixing(TenderDetailsMixing):
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
        super().on_patch(before, after)


class TenderDetailsState(BelowThresholdTenderDetailsMixing, BelowThresholdTenderState):
    pass
