# -*- coding: utf-8 -*-
from logging import getLogger
from uuid import uuid4

from schematics.types import BaseType, MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType

LOGGER = getLogger(__name__)


class RequirementReference(Model):
    id = StringType(required=True)
    title = StringType()


class RequirementResponse(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    requirement = ModelType(RequirementReference, required=True)
    value = BaseType()  # Maybe there better way to use BaseType(in Requirement too)
    values = ListType(BaseType(required=True))
