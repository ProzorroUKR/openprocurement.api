import logging
from decimal import Decimal

from openprocurement.api.utils import error_handler, context_unpack, raise_operation_error
from openprocurement.tender.cfaselectionua.procedure.utils import equals_decimal_and_corrupted
from openprocurement.tender.core.procedure.utils import get_supplier_contract
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.context import get_now

logger = logging.getLogger(__name__)


class BidState(BaseState):
    update_date_on_value_amount_change_enabled = True

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def on_post(self, data):
        now = get_now().isoformat()
        data["date"] = now

        self.validate_status(data)
        self.validate_bid_vs_agreement(data)
        self.validate_items_id(data)

        lot_values = data.get("lotValues")
        if lot_values:  # TODO: move to post model as serializible
            for lot_value in lot_values:
                lot_value["date"] = now

        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_status_change(before, after)
        self.validate_bid_vs_agreement(after)
        self.update_date_on_value_amount_change(before, after)
        self.validate_items_id(after)
        super().on_patch(before, after)

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

        agreement = self.request.registry.mongodb.agreements.get(tender["agreements"][0]["id"])
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
        tender_items_id = {i["id"] for i in self.request.validated["tender"].get("items", "")}
        bid_items_id = {i["id"] for i in after.get("items", "")}

        if bid_items_id - tender_items_id:
            raise_operation_error(self.request, "Bid items ids should be on tender items ids", status=422)
