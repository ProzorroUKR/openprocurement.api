from schematics.exceptions import ValidationError

from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_agreement
from openprocurement.api.utils import raise_operation_error

# changes modifications validators


def validate_modifications_items_uniq(modifications):
    agreement = get_request().validated["agreement"]
    if modifications:
        agreement_items_id = {item["id"] for item in agreement.get("items", [])}
        item_ids = {m.itemId for m in modifications if m.itemId in agreement_items_id}
        if len(item_ids) != len(modifications):
            raise ValidationError("Item id should be uniq for all modifications and one of agreement:items")


def validate_modifications_contracts_uniq(modifications):
    agreement = get_request().validated["agreement"]
    if modifications:
        agreement_contracts_id = {contract["id"] for contract in agreement.get("contracts")}
        contracts_ids = {mod["contractId"] for mod in modifications if mod["contractId"] in agreement_contracts_id}
        if len(contracts_ids) != len(modifications):
            raise ValidationError("Contract id should be uniq for all modifications and one of agreement:contracts")


def validate_related_item(related_item: str, document_of: str) -> None:
    if document_of not in ["item", "change", "contract"]:
        return

    if not related_item:
        raise_operation_error(
            get_request(),
            "This field is required.",
            name="documents.relatedItem",
            status=422,
        )

    if parent_obj := get_agreement():
        container = document_of + "s"
        if not any(i and related_item == i["id"] for i in parent_obj.get(container, "")):
            raise_operation_error(
                get_request(),
                f"relatedItem should be one of {container}",
                name="documents.relatedItem",
                status=422,
            )
