from openprocurement.tender.competitivedialogue.procedure.state.stage2.eu_tender_details import (
    CDEUTenderDetailsState,
)
from openprocurement.tender.openua.constants import TENDERING_DURATION


class CDUATenderDetailsState(CDEUTenderDetailsState):
    tendering_duration = TENDERING_DURATION

    @staticmethod
    def watch_value_meta_changes(tender):
        pass
