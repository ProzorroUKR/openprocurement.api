from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import ListType


class LotId(Model):
    id = StringType()


class Firms(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(LotId, required=True))


def validate_shortlisted_firm_ids(data, firms):
    lot_ids = {e["id"] for e in data.get("lots") or ""}
    for f in firms:
        for lot in f.get("lots") or "":
            lot_id = lot.get("id")
            if lot_id and lot_id not in lot_ids:
                raise ValidationError("id should be one of lots")
