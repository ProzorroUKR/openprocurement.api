from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.pricequotation.procedure.models.contract import Contract


class PriceQuotationTenderState(TenderState):
    contract_model = Contract
    award_class = Award
    generate_award_milestones = False

    def get_events(self, tender):
        status = tender["status"]

        if status == "active.tendering":
            if tender.get("tenderPeriod", {}).get("endDate"):
                yield tender["tenderPeriod"]["endDate"], self.tendering_end_handler

        yield from self.contract_events(tender)

    def add_next_contract_handler(self, award):
        def handler(*_):
            request = get_request()
            pq_add_contracts(request, award)
            self.add_next_award()

        return handler
