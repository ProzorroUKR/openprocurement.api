from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.procedure.context import get_contract, get_tender
from openprocurement.contracting.core.procedure.models.document import (
    Document as BaseDocument,
)
from openprocurement.contracting.core.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.contracting.core.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument):
    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class PatchDocument(BasePatchDocument):
    pass


class Document(BaseDocument):
    confidentiality = StringType(choices=["public", "buyerOnly"])

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


def is_obj_exist(parent_obj: dict, obj_id: str, container: str) -> bool:
    return any(i and obj_id == i["id"] for i in parent_obj.get(container, ""))


def validate_relatedItem(related_item: str, document_of: str) -> None:
    if document_of not in ["item", "change", "lot"]:
        return

    if not related_item:
        raise ValidationError("This field is required.")

    if document_of == "lot":
        parent_obj = get_tender()
    else:
        parent_obj = get_contract()

    if not parent_obj:
        return

    container = document_of + "s"

    if not is_obj_exist(parent_obj, related_item, container):
        raise ValidationError(f"relatedItem should be one of {container}")
