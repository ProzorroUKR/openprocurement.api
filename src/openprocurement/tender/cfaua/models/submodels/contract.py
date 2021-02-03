# -*- coding: utf-8 -*-
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.transforms import blacklist
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    BusinessOrganization,
    schematics_default_role,
    schematics_embedded_role,
)
from openprocurement.tender.core.models import validate_parameters_uniq
from openprocurement.tender.cfaua.models.submodels.unitprice import UnitPrice
from openprocurement.tender.cfaua.models.submodels.parameters import Parameter


class Contract(Model):
    class Options:
        roles = {
            "create": blacklist(),
            "edit": blacklist("id", "suppliers", "date", "awardID", "bidID"),
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
    status = StringType(choices=["active", "unsuccessful"], default="active")
    suppliers = ListType(ModelType(BusinessOrganization, required=True))
    unitPrices = ListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()

    def validate_awardID(self, data, awardID):
        parent = data["__parent__"]
        if awardID and isinstance(parent, Model) and awardID not in [i.id for i in parent["__parent__"].awards]:
            raise ValidationError("awardID should be one of awards")
