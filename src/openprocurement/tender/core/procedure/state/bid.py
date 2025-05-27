import logging
from collections import defaultdict
from decimal import Decimal

from schematics.types import BaseType

from openprocurement.api.constants_env import (
    BID_ITEMS_PRODUCT_REQUIRED_FROM,
    ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM,
    REQ_RESPONSE_VALUES_VALIDATION_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_object, get_tender
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import (
    error_handler,
    get_tender_product,
    raise_operation_error,
)
from openprocurement.tender.cfaselectionua.procedure.utils import (
    equals_decimal_and_corrupted,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.utils import (
    get_supplier_contract,
    is_bid_items_required,
    tender_created_after,
)
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_doc_type_required,
    validate_items_unit_amount,
    validate_req_response_values,
    validate_required_fields,
    validate_signer_info_container,
)

logger = logging.getLogger(__name__)


class BidState(BaseState):
    items_unit_value_required_for_funders = False
    items_product_required = False

    @property
    def check_all_exist_tender_items(self):
        return is_bid_items_required()

    def status_up(self, before, after, data):
        if before in ("draft", "invalid") and after == "pending":
            self.validate_proposal_doc_required(data)
        super().status_up(before, after, data)

    def on_post(self, data):
        now = get_request_now().isoformat()
        data["date"] = now
        self.validate_items_required_field(data)
        self.validate_tenderers_signer_info(data)
        self.validate_bid_unit_value(data)
        self.validate_status(data)
        self.validate_bid_vs_agreement(data)
        self.validate_items_id(data)
        self.validate_items_related_product(data, {})
        self.validate_proposal_docs(data)
        self.validate_req_responses(data)

        lot_values = data.get("lotValues")
        if lot_values:  # TODO: move to post model as serializible
            for lot_value in lot_values:
                lot_value["date"] = now

        super().on_post(data)

    def on_patch(self, before, after):
        self.validate_items_required_field(after)
        self.validate_tenderers_signer_info(after)
        self.lot_values_patch_keep_unchange(after, before)
        self.validate_bid_unit_value(after)
        self.validate_status_change(before, after)
        self.update_date_for_new_lot_values(after, before)
        self.validate_items_id(after)
        self.validate_items_related_product(after, before)
        self.validate_proposal_docs(after, before)
        self.invalidate_pending_bid_after_patch(after, before)
        self.validate_req_responses(after)
        super().on_patch(before, after)

    def raise_items_error(self, message):
        raise_operation_error(
            self.request,
            message,
            status=422,
            location="body",
            name="items",
        )

    def validate_bid_unit_value(self, data):
        tender = get_tender()
        items_for_lot = False
        tender_items_id = {}
        tender_lot_id = {}

        tender_items = tender.get("items", [])
        if lot_values := data.get("lotValues"):
            tender_lot_id = {item["id"]: item["relatedLot"] for item in tender_items if item.get("relatedLot")}
            items_unit_value_amount = defaultdict(lambda: [])
            lot_values_by_id = {}
            for lot_value in lot_values:
                tender_items_id[lot_value["relatedLot"]] = {
                    tender_item["id"]
                    for tender_item in tender_items
                    if tender_item.get("relatedLot") == lot_value["relatedLot"]
                }
                lot_values_by_id[lot_value["relatedLot"]] = lot_value
            items_for_lot = True
        else:
            items_unit_value_amount = []

        if data.get("items"):
            for item in data["items"]:
                if value := item.get("unit", {}).get("value"):
                    if tender_created_after(ITEMS_UNIT_VALUE_AMOUNT_VALIDATION_FROM):
                        if value.get("valueAddedTaxIncluded"):
                            self.raise_items_error(
                                "valueAddedTaxIncluded of bid unit should be False",
                            )
                    elif items_for_lot:
                        lot_id = tender_lot_id.get(item["id"])
                        if (lot_value := lot_values_by_id.get(lot_id)) and lot_value.get("value"):
                            if lot_value["value"].get("valueAddedTaxIncluded") is not None and lot_value["value"].get(
                                "valueAddedTaxIncluded"
                            ) != value.get("valueAddedTaxIncluded"):
                                self.raise_items_error(
                                    "valueAddedTaxIncluded of bid unit should be identical "
                                    "to valueAddedTaxIncluded of bid lotValues",
                                )
                    elif bid_value := data.get("value", {}):
                        if bid_value.get("valueAddedTaxIncluded") is not None and bid_value.get(
                            "valueAddedTaxIncluded"
                        ) != value.get("valueAddedTaxIncluded"):
                            self.raise_items_error(
                                "valueAddedTaxIncluded of bid unit should be identical "
                                "to valueAddedTaxIncluded of bid value",
                            )

                    if tender_value := tender.get("value", {}):
                        if tender["config"]["valueCurrencyEquality"] is True and tender_value.get(
                            "currency"
                        ) != value.get("currency"):
                            self.raise_items_error(
                                "currency of bid unit should be identical to currency of tender value"
                            )
                    if item.get("quantity") is not None:
                        if item["quantity"] == 0 and item["unit"]["value"]["amount"] != 0:
                            self.raise_items_error(
                                "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0"
                            )
                        if items_for_lot:
                            for lot_id, items_ids in tender_items_id.items():
                                if item["id"] in items_ids:
                                    items_unit_value_amount[lot_id].append(
                                        to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                                    )
                                    break
                        else:
                            items_unit_value_amount.append(
                                to_decimal(item["quantity"]) * to_decimal(item["unit"]["value"]["amount"])
                            )

                elif self.items_unit_value_required_for_funders and tender.get("funders"):
                    self.raise_items_error("items.unit.value is required for tender with funders")
        elif self.items_unit_value_required_for_funders and tender.get("funders"):
            self.raise_items_error("items is required for tender with funders")

        if items_for_lot:
            for lot_id, items_ids in items_unit_value_amount.items():
                validate_items_unit_amount(items_ids, lot_values_by_id[lot_id], obj_name="bid.lotValues")
        else:
            validate_items_unit_amount(items_unit_value_amount, data, obj_name="bid")

    def validate_proposal_doc_required(self, bid):
        if bid["tenderers"][0].get("identifier", {}).get("scheme") == "UA-EDR":
            validate_doc_type_required(
                bid.get("documents", []),
                document_type="proposal",
                document_of="tender",
                after_date=bid.get("submissionDate"),
            )
        now = get_request_now().isoformat()
        bid["submissionDate"] = bid["date"] = now
        for lot_value in bid.get("lotValues", []):
            lot_value["date"] = now

    def validate_proposal_docs(self, data, before=None):
        for key in (
            "documents",
            "financialDocuments",
            "eligibilityDocuments",
            "qualificationDocuments",
        ):
            documents = data.get(key, [])
            if before is None or before and len(before.get(key, [])) != len(documents):
                validate_doc_type_quantity(documents, document_type="proposal", obj_name="bid")

    def invalidate_pending_bid_after_patch(self, after, before):
        if self.request.authenticated_role == "Administrator":
            return
        if before.get("status") == after.get("status") == "pending" and before != after:
            after["status"] = "invalid"

    def validate_req_responses(self, data):
        if get_request_now() > REQ_RESPONSE_VALUES_VALIDATION_FROM:
            for resp in data.get("requirementResponses", []):
                validate_req_response_values(resp)

    def update_date_for_new_lot_values(self, after, before):
        now = get_request_now().isoformat()
        for after_lot in after.get("lotValues") or []:
            for before_lot in before.get("lotValues") or []:
                if before_lot["relatedLot"] == after_lot["relatedLot"]:
                    after_lot["date"] = before_lot.get("date", now)
                    break
            else:  # lotValue has been just added
                after_lot["date"] = get_request_now().isoformat()

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
        if status == "pending":
            self.validate_proposal_doc_required(data)

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
            raise_operation_error(
                self.request,
                "Bid value.amount can't be greater than contact value.amount.",
            )

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

        check_all_tender_items = self.check_all_exist_tender_items or (
            self.items_unit_value_required_for_funders and self.request.validated["tender"].get("funders")
        )

        if check_all_tender_items and tender_items_id - bid_items_id:
            raise_operation_error(
                self.request,
                f"Bid items ids should include all tender items ids{' for current lot' if items_for_lot else ''}",
                status=422,
            )

    def validate_items_required_field(self, after: dict):
        tender = self.request.validated["tender"]
        tender_items = {item["id"]: item for item in tender.get("items", [])}
        bid_items = {item["id"]: item for item in after.get("items", [])}

        if not is_bid_items_required() or not tender_items:
            return

        if tender_items and not bid_items:
            self.raise_items_error(BaseType.MESSAGES["required"])

        item_required_fields = {
            "description": True,
            "unit": {
                "name": True,
                "code": True,
            },
            "quantity": True,
        }
        if tender["procurementMethodType"] == "esco":
            item_required_fields = {
                "description": True,
                "unit": {
                    "__required__": False,
                    "name": True,
                    "code": True,
                },
            }

        for item_id, item in bid_items.items():
            # product is required for tender item with category
            if (
                tender_created_after(BID_ITEMS_PRODUCT_REQUIRED_FROM)
                and self.items_product_required
                and (tender_item := tender_items.get(item_id))
            ):
                item_required_fields["product"] = bool(tender_item.get("category"))
            validate_required_fields(self.request, item, item_required_fields, name="items")

    def validate_items_related_product(self, after: dict, before: dict) -> None:
        after_items_rps = {item["id"]: item.get("product", "") for item in after.get("items", "")}
        before_items_rps = {item["id"]: item.get("product", "") for item in before.get("items", "")}

        for item_id, after_rp in after_items_rps.items():
            if after_rp:
                if not (before_rp := before_items_rps.get(item_id)) or before_rp != after_rp:
                    get_tender_product(get_request(), after_rp, ("active",))

    def lot_values_patch_keep_unchange(self, after: dict, before: dict):
        fields_keep_unchanged = ("weightedValue", "date", "status")

        after_lot_values = after.get("lotValues", [])
        before_lot_values = before.get("lotValues", [])

        for lot_values in zip(after_lot_values, before_lot_values):
            for field in fields_keep_unchanged:
                if lot_values[0].get(field) != lot_values[1].get(field):
                    if not lot_values[1].get(field):
                        lot_values[0].pop(field, None)
                    else:
                        lot_values[0][field] = lot_values[1][field]

    def validate_tenderers_signer_info(self, bid):
        tender = self.request.validated["tender"]
        validate_signer_info_container(self.request, tender, bid.get("tenderers"), "tenderers")
