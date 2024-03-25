import logging
from decimal import Decimal

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_object, get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import (
    context_unpack,
    error_handler,
    raise_operation_error,
)
from openprocurement.tender.cfaselectionua.procedure.utils import (
    equals_decimal_and_corrupted,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import get_supplier_contract

logger = logging.getLogger(__name__)


class BidState(BaseState):
    update_date_on_value_amount_change_enabled = True
    items_unit_value_required_for_funders = False

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def on_post(self, data):
        now = get_now().isoformat()
        data["date"] = now

        self.validate_bid_unit_value(data)
        self.validate_status(data)
        self.validate_bid_vs_agreement(data)
        self.validate_items_id(data)

        lot_values = data.get("lotValues")
        if lot_values:  # TODO: move to post model as serializible
            for lot_value in lot_values:
                lot_value["date"] = now

        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_bid_unit_value(after)
        self.validate_status_change(before, after)
        self.update_date_on_value_amount_change(before, after)
        self.validate_items_id(after)
        super().on_patch(before, after)

    def validate_bid_unit_value(self, data):
        tender = get_tender()

        def raise_items_error(message):
            raise_operation_error(
                self.request,
                message,
                status=422,
                location="body",
                name="items",
            )

        if data.get("items"):
            for item in data["items"]:
                if value := item.get("unit", {}).get("value"):
                    if tender.get("value", {}).get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
                        raise_items_error(
                            "valueAddedTaxIncluded of bid unit should be identical to valueAddedTaxIncluded of tender value",
                        )
                    if tender["config"]["valueCurrencyEquality"] is True and tender.get("value", {}).get(
                        "currency"
                    ) != value.get("currency"):
                        raise_items_error("currency of bid unit should be identical to currency of tender value")
                elif self.items_unit_value_required_for_funders and tender.get("funders"):
                    raise_items_error("items.unit.value is required for tender with funders")
        elif self.items_unit_value_required_for_funders and tender.get("funders"):
            raise_items_error("items is required for tender with funders")

    def update_date_on_value_amount_change(self, before, after):
        if not self.update_date_on_value_amount_change_enabled:
            return
        now = get_now().isoformat()
        # if value.amount is going to be changed -> update "date"
        amount_before = (before.get("value") or {}).get("amount")
        amount_after = (after.get("value") or {}).get("amount")
        if amount_before != amount_after:
            logger.info(
                f"Bid value amount changed from {amount_before} to {amount_after}",
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "bid_amount_changed"},
                    {
                        "BID_ID": after["id"],
                    },
                ),
            )
            after["date"] = get_now().isoformat()
        # the same as above, for lots
        for after_lot in after.get("lotValues") or []:
            for before_lot in before.get("lotValues") or []:
                if before_lot["relatedLot"] == after_lot["relatedLot"]:
                    if float(before_lot["value"]["amount"]) != after_lot["value"]["amount"]:
                        logger.info(
                            f'Bid lot value amount changed from {before_lot["value"]["amount"]} to {after_lot["value"]["amount"]}',
                            extra=context_unpack(
                                get_request(),
                                {"MESSAGE_ID": "bid_amount_changed"},
                                {
                                    "BID_ID": after["id"],
                                    "LOT_ID": after_lot["relatedLot"],
                                },
                            ),
                        )
                        after_lot["date"] = now
                    else:
                        # all data in save_tender applied by json_patch logic
                        # which means list items applied by position
                        # so when we change order of relatedLot in lotValues
                        # this don't affect "date" fields that stays on the same positions
                        # this causes bugs: missed date and wrong date values
                        # This else statement ensures that wherever relatedLot goes,
                        # its "date" goes with it
                        after_lot["date"] = before_lot.get("date", now)
                    break
            else:  # lotValue has been just added
                after_lot["date"] = get_now().isoformat()

    def validate_status_change(self, before, after):
        if self.request.authenticated_role == "Administrator":
            return

        allowed_status = "pending"
        status_before = before.get("status")
        status_after = after.get("status")
        if status_before != status_after and status_after != allowed_status:
            self.request.errors.add(
                "body",
                "bid",
                "Can't update bid to ({}) status".format(status_after),
            )
            self.request.errors.status = 403
            raise error_handler(self.request)

    def validate_status(self, data):
        allowed_statuses = ("draft", "pending")
        status = data.get("status")
        if status not in allowed_statuses:
            self.request.errors.add(
                "body",
                "bid",
                "Bid can be added only with status: {}".format(allowed_statuses),
            )
            self.request.errors.status = 403
            raise error_handler(self.request)

    def validate_bid_vs_agreement(self, data):
        tender = get_tender()

        if not tender["config"]["hasPreSelectionAgreement"]:
            return

        agreement = get_object("agreement")
        supplier_contract = get_supplier_contract(
            agreement["contracts"],
            data["tenderers"],
        )

        self.validate_bid_with_contract(data, supplier_contract)

    def validate_bid_with_contract(self, data, supplier_contract):
        if not supplier_contract:
            raise_operation_error(self.request, "Bid is not a member of agreement")

        if (
            data.get("lotValues")
            and supplier_contract.get("value")
            and Decimal(data["lotValues"][0]["value"]["amount"]) > Decimal(supplier_contract["value"]["amount"])
        ):
            raise_operation_error(self.request, "Bid value.amount can't be greater than contact value.amount.")

        if data.get("parameters"):
            contract_parameters = {p["code"]: p["value"] for p in supplier_contract.get("parameters", "")}
            for p in data["parameters"]:
                code = p["code"]
                if code not in contract_parameters or not equals_decimal_and_corrupted(
                    Decimal(p["value"]), contract_parameters[code]
                ):
                    raise_operation_error(self.request, "Can't post inconsistent bid")

    def validate_items_id(self, after: dict) -> None:
        items_for_lot = False
        tender_items = self.request.validated["tender"].get("items", [])
        if lot_values := after.get("lotValues"):
            lot_ids = {lot_value["relatedLot"] for lot_value in lot_values}
            tender_items_id = {item["id"] for item in tender_items if item.get("relatedLot") in lot_ids}
            items_for_lot = True
        else:
            tender_items_id = {i["id"] for i in tender_items}
        bid_items_id = {i["id"] for i in after.get("items", "")}

        if bid_items_id - tender_items_id:
            raise_operation_error(
                self.request,
                f"Bid items ids should be on tender items ids{' for current lot' if items_for_lot else ''}",
                status=422,
            )
        if self.request.validated["tender"].get("funders") and tender_items_id - bid_items_id:
            raise_operation_error(
                self.request,
                f"Bid items ids should include all tender items ids{' for current lot' if items_for_lot else ''}",
                status=422,
            )
