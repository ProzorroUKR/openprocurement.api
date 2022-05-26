# -*- coding: utf-8 -*-
from uuid import uuid4

from schematics.types.compound import ModelType
from schematics.types import MD5Type
from openprocurement.api.models import Model, ListType
from schematics.types import StringType, BaseType

from logging import getLogger

LOGGER = getLogger(__name__)


class RequirementReference(Model):
    id = StringType(required=True)
    title = StringType()


class RequirementResponse(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    requirement = ModelType(RequirementReference, required=True)
    value = BaseType()  # Maybe there better way to use BaseType(in Requirement too)
    values = ListType(BaseType(required=True))
