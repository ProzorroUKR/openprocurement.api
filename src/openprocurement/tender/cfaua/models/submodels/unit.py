# -*- coding: utf-8 -*-
from openprocurement.api.models import Unit as BaseUnit
from openprocurement.tender.cfaua.models.submodels.value import Value
from schematics.types.compound import ModelType


class Unit(BaseUnit):
    value = ModelType(Value)
