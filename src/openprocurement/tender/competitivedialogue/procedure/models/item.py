from typing import ClassVar

from openprocurement.api.procedure.models.item import CPVClassification
from openprocurement.tender.core.procedure.models.item import Item


class CDCPVClassification(CPVClassification):
    dk021_scheme_required: ClassVar[bool] = False


class CDItem(Item):
    classification: CDCPVClassification
