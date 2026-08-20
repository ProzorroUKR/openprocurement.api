from openprocurement.api.context import get_request
from openprocurement.tender.core.procedure.contracting import (
    add_contracts,
    append_contracts_added,
)
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

    def add_next_contract_handler(self, award):
        def handler(*_):
            request = get_request()
            contracts = add_contracts(request, award)
            self.add_next_award()
            append_contracts_added(request, contracts)

        return handler
