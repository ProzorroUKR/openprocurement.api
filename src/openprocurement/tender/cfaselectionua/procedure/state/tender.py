from openprocurement.tender.core.procedure.context import get_tender_config
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import validate_field


class CFASelectionTenderState(TenderState):
    min_bids_number = 1

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

    def validate_minimal_step(self, data, before=None):
        # override to skip minimalStep required validation
        # it's not required for cfaselectionua in tender level
        config = get_tender_config()
        kwargs = {
            "before": before,
            "enabled": config.get("hasAuction") is True,
        }
        validate_field(data, "minimalStep", required=False, **kwargs)
