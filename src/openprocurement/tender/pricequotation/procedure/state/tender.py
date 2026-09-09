from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.tender import TenderState


class PriceQuotationTenderState(TenderState):
    award_class = Award
    generate_award_milestones = False
    award_period_duration = 2

    def get_events(self, tender, enable_approve_check=False):
        status = tender["status"]

        if status == "active.tendering":
            if tender.get("tenderPeriod", {}).get("endDate"):
                yield tender["tenderPeriod"]["endDate"], self.tendering_end_handler

        yield from self.contract_events(tender)
