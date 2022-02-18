from openprocurement.tender.core.models import validate_values_uniq
from openprocurement.api.models import Model, ListType
from schematics.types import StringType, FloatType
from schematics.types.compound import ModelType
from schematics.validate import ValidationError
from uuid import uuid4


class FeatureValue(Model):
    value = FloatType(required=True, min_value=0.0, max_value=0.3)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()


class Feature(Model):
    code = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    featureOf = StringType(required=True, choices=["tenderer", "lot", "item"], default="tenderer")
    relatedItem = StringType(min_length=1)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    enum = ListType(
        ModelType(FeatureValue, required=True),
        default=list(),
        min_size=1,
        validators=[validate_values_uniq],
    )


def validate_related_items(data, features):
    if features:
        item_ids = {i.id for i in data.get("items") or []}
        lot_ids = {i.id for i in data.get("lots") or []}

        for f in features:
            related_item = f.relatedItem
            feature_of = f.featureOf
            if not related_item and feature_of in ("item", "lot"):
                raise ValidationError([{'relatedItem': ['This field is required.']}])

            if feature_of == "item":
                if f.relatedItem not in item_ids:
                    raise ValidationError([{'relatedItem': ["relatedItem should be one of items"]}])

            elif feature_of == "lot" and f.relatedItem not in lot_ids:
                raise ValidationError([{'relatedItem': ["relatedItem should be one of lots"]}])
