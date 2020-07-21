from schematics.types import StringType
from schematics.exceptions import ValidationError
from openprocurement.tender.core.models import BaseDocument, Model, get_tender


class Document(BaseDocument):
    documentOf = StringType(
        required=True,
        choices=["tender", "item"],
        default="tender"
    )

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("documentOf") in ["item"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        if relatedItem and isinstance(parent, Model):
            tender = get_tender(parent)
            items = [i.id for i in tender.items if i]
            if data.get("documentOf") == "item" and relatedItem not in items:
                raise ValidationError(u"relatedItem should be one of items")
