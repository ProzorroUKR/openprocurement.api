from decimal import Decimal

from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.arma.procedure.models.bid import (
    PatchBid,
    PatchQualificationBid,
)
from openprocurement.tender.core.procedure.state.bid import BidState as BaseBidState
from openprocurement.tender.core.procedure.utils import get_supplier_contract


class BidState(BaseBidState):
    item_patch_fields_during_qualification = {
        "requirementResponses": None,
        "subcontractingDetails": None,
        "tenderers": ("signerInfo",),
        "lotValues": ("subcontractingDetails",),
    }
    check_item_unit_amount = False

    def validate_bid_with_contract(self, data, agreement):
        supplier_contract = get_supplier_contract(
            agreement["contracts"],
            data["tenderers"],
        )

        if not supplier_contract:
            raise_operation_error(self.request, "Bid is not a member of agreement")

        if (
            data.get("lotValues")
            and supplier_contract.get("value")
            and Decimal(data["lotValues"][0]["value"]["amountPercentage"])
            > Decimal(supplier_contract["value"]["amountPercentage"])
        ):
            raise_operation_error(
                self.request,
                "Bid value.amountPercentage can't be greater than contract value.amountPercentage.",
            )

    def execute_unit_validation(self, items_for_lot, items_unit_value_amount, lot_values_by_id, data):
        pass

    def get_patch_data_model(self):
        tender = self.request.validated["tender"]
        if tender.get("status", "") in self.qualification_statuses:
            return PatchQualificationBid
        return PatchBid
