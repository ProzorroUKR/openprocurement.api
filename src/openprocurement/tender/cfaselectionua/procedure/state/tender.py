from openprocurement.tender.core.procedure.state.tender import TenderState


class CFASelectionTenderState(TenderState):

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
            "valueAddedTaxIncluded": tender["lots"][0]["value"]["valueAddedTaxIncluded"]
        }

    def calc_tender_minimal_step(self, tender: dict) -> None:
        if not all(i.get("minimalStep") for i in tender.get("lots", "")):
            return
        tender["minimalStep"] = {
            "amount": min(i["minimalStep"]["amount"] for i in tender["lots"] if i.get("minimalStep")),
            "currency": tender["lots"][0]["minimalStep"]["currency"],
            "valueAddedTaxIncluded": tender["lots"][0]["minimalStep"]["valueAddedTaxIncluded"],
        }
