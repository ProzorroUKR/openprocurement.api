# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import (
    BaseAward,
    WeightedValueMixin,
)
from schematics.exceptions import ValidationError
from schematics.types import MD5Type
from openprocurement.api.models import Model


class Award(BaseAward, WeightedValueMixin):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """

    class Options:
        roles = RolesFromCsv("Award.csv", relative_to=__file__)

    bid_id = MD5Type(required=True)
    lotID = MD5Type()

    def validate_lotID(self, data, lotID):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            if not lotID and parent.lots:
                raise ValidationError("This field is required.")
            if lotID and lotID not in [lot.id for lot in parent.lots if lot]:
                raise ValidationError("lotID should be one of lots")
