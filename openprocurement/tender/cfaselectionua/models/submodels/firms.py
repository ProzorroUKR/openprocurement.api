# -*- coding: utf-8 -*-
from schematics.types import StringType
from openprocurement.api.models import (
    Identifier, Model
)

from schematics.types.compound import ModelType


class Firms(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
