from openprocurement.tender.core.procedure.state.tender import TenderState


class CFASelectionTenderState(TenderState):
    generate_award_milestones = False

    def lots_qualification_events(self, tender):
        yield from ()  # no qualification events

    def lots_awarded_events(self, tender):
        yield from ()  # no awarded events

    def calc_tender_value(self, tender: dict) -> None:
        if not all(i.get("value") for i in tender.get("lots", "")):
            return
        tender["value"] = {
            "amount": sum(i["value"]["amount"] for i in tender["lots"]),
            "currency": tender["lots"][0]["value"]["currency"],
            "valueAddedTaxIncluded": tender["lots"][0]["value"]["valueAddedTaxIncluded"],
        }
