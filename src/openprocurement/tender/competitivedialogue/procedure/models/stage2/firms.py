from openprocurement.tender.core.procedure.models.organization import Identifier
from openprocurement.api.models import ListType, Model, ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType


class LotId(Model):
    id = StringType()


class Firms(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(LotId, required=True))


def validate_shortlisted_firm_ids(data, firms):
    lot_ids = {e["id"] for e in data.get("lots") or ""}
    for f in firms:
        for l in f.get("lots") or "":
            lot_id = l.get("id")
            if lot_id and lot_id not in lot_ids:
                raise ValidationError("id should be one of lots")
