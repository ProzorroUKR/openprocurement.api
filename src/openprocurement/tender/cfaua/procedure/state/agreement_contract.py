from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.api.utils import raise_operation_error, to_decimal
from openprocurement.api.validation import OPERATIONS
from decimal import Decimal


class AgreementContractStateMixing:

    def agreement_contract_on_patch(self, before, after):
        if before["status"] != after["status"]:
            self.agreement_contract_status_up(before["status"], after["status"], after)

    def agreement_contract_status_up(self, before, after, agreement):
        pass

    # Validators
    def validate_agreement_contract_on_patch(self, before, after):
        request, tender = get_request(), get_tender()
        self.validate_agreement_operation_not_in_allowed_status(request, tender)
        self.validate_agreement_contract_unitprices_update(request, tender, before, after)

    @staticmethod
    def validate_agreement_operation_not_in_allowed_status(request, tender):
        if tender['status'] != "active.awarded":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} agreement in current ({tender['status']}) tender status"
            )

    @staticmethod
    def validate_agreement_contract_unitprices_update(request, tender, before, contract):
        # TODO: refactoring
        agreement_items_id = {u.get("relatedItem") for u in before.get("unitPrices", "")}
        validated_items_id = {
            u["relatedItem"]
            for u in contract.get("unitPrices", "")
            if u.get("value", {}).get("amount") is not None
        }
        agreement = request.validated["agreement"]
        quantity_cache = {i["id"]: to_decimal(i["quantity"]) for i in agreement.get("items")}

        if contract["status"] == "active" or "unitPrices" in request.validated["json_data"]:
            if len(agreement_items_id) != len(validated_items_id):
                raise_operation_error(request, "unitPrice.value.amount count doesn't match with contract.", status=422)
            if agreement_items_id != validated_items_id:
                raise_operation_error(request, "All relatedItem values doesn't match with contract.", status=422)

            unit_price_amounts = []
            for unit_price in contract.get("unitPrices", ""):
                if unit_price.get("value", {}).get("currency") != tender["value"]["currency"]:
                    raise_operation_error(
                        request,
                        "currency of bid should be identical to currency of value of lot",
                        status=422,
                    )
                if unit_price.get("value", {}).get("valueAddedTaxIncluded") != tender["value"]["valueAddedTaxIncluded"]:
                    raise_operation_error(
                        request,
                        "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot",
                        status=422,
                    )
                quantity = quantity_cache[unit_price.get("relatedItem")]
                unit_price_amounts.append(quantity * to_decimal(unit_price["value"]["amount"]))

            bid = [b for b in tender.get("bids", "") if b["id"] == before["bidID"]][0]
            award_lot_id = [a for a in tender.get("awards", "") if a["id"] == before["awardID"]][0].get("lotID")
            if award_lot_id:
                value = [v for v in bid["lotValues"] if v["relatedLot"] == award_lot_id][0]["value"]["amount"]
                error_field = "bid.lotValue.value.amount"
            else:
                value = bid["value"]["amount"]
                error_field = "bid.value.amount"

            value = to_decimal(value)

            if sum(unit_price_amounts) > value:
                raise_operation_error(request, f"Total amount can't be greater than {error_field}", status=422)


class AgreementContractState(AgreementContractStateMixing, TenderState):
    pass
