from openprocurement.api.context import get_now
from openprocurement.tender.openeu.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION as EU_TENDERING_DURATION
)
from openprocurement.tender.openua.constants import (
    TENDERING_DURATION as UA_TENDERING_DURATION
)


class CDEUTenderDetailsState(TenderDetailsState):
    tendering_duration = EU_TENDERING_DURATION

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


class CDUATenderDetailsState(CDEUTenderDetailsState):
    tendering_duration = UA_TENDERING_DURATION

    @staticmethod
    def watch_value_meta_changes(tender):
        pass
