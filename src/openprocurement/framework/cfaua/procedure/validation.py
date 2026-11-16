from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_agreement
from openprocurement.api.utils import raise_operation_error

# changes modifications validators


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
