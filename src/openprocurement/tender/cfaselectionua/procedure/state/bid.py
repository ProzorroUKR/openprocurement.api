from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState
from openprocurement.tender.core.procedure.utils import get_supplier_contract


class BidState(BaseBidState):
    def validate_bid_vs_agreement(self, data):
        # cfaselectionua has agreements full copy in tender.agreements
        supplier_contract = get_supplier_contract(
            get_tender()["agreements"][0]["contracts"],
            data["tenderers"],
        )
        self.validate_bid_with_contract(data, supplier_contract)

    def on_patch(self, before, after):
        self.validate_bid_vs_agreement(after)
        super().on_patch(before, after)
