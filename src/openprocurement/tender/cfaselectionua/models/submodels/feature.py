# -*- coding: utf-8 -*-
from uuid import uuid4
from decimal import Decimal
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType
from openprocurement.api.models import Model, DecimalType
from openprocurement.agreement.cfaua.validation import validate_values_uniq


class FeatureValue(Model):
    value = DecimalType(required=True, min_value=Decimal('0.0'), max_value=Decimal('0.3'))
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()


class Feature(Model):
    code = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    featureOf = StringType(required=True, choices=['tenderer', 'lot', 'item'], default='tenderer')
    relatedItem = StringType(min_length=1)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    enum = ListType(ModelType(FeatureValue), default=list(), min_size=1, validators=[validate_values_uniq])

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get('featureOf') in ['item', 'lot']:
            raise ValidationError(u'This field is required.')
        if data.get('featureOf') == 'item' and isinstance(data['__parent__'], Model) and \
                relatedItem not in [i.id for i in data['__parent__'].items]:
            raise ValidationError(u"relatedItem should be one of items")
        if data.get('featureOf') == 'lot' and isinstance(data['__parent__'], Model) and \
                relatedItem not in [i.id for i in data['__parent__'].lots]:
            raise ValidationError(u"relatedItem should be one of lots")
