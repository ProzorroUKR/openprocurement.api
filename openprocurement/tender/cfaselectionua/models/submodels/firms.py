# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from openprocurement.api.models import (
    Identifier, Model
)

from schematics.types.compound import ModelType


class Firms(Model):
    class Options:
        roles = RolesFromCsv('Firms.csv', relative_to=__file__)
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
