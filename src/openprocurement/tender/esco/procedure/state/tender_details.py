from openprocurement.tender.core.utils import calculate_complaint_business_date
from openprocurement.tender.esco.constants import COMPLAINT_SUBMIT_TIME
from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.openeu.procedure.state.tender_details import TenderDetailsState as BaseTenderDetailsState


class TenderDetailsState(BaseTenderDetailsState):

    def on_post(self, tender):
        super().on_post(tender)
        self.update_periods(tender)

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
