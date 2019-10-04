# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import Item as BaseItem, Address, PeriodEndRequired


class AgreementItem(BaseItem):
    """A good, service, or work to be contracted."""

    class Options:
        roles = RolesFromCsv("AgreementItem.csv", relative_to=__file__)

    description_en = StringType(required=True, min_length=1)
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)
