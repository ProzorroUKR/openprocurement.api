from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.openeu.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.openeu.constants import TENDERING_DURATION


class CDEUTenderDetailsState(TenderDetailsState):
    tendering_duration = TENDERING_DURATION

    @staticmethod
    def watch_value_meta_changes(tender):
        pass

    def on_post(self, tender):
        tender["tenderPeriod"] = {
            "startDate": get_now().isoformat(),
            "endDate": calculate_tender_business_date(
                get_now(),
                self.tendering_duration,
                tender=tender
            ).isoformat()
        }

        super().on_post(tender)
