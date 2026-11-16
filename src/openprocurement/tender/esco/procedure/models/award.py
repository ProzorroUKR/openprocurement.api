from openprocurement.tender.core.procedure.models.award import Award, PostAward
from openprocurement.tender.esco.procedure.models.value import ESCOValue, ESCOWeightedValue


class ESCOAward(Award):
    value: ESCOValue | None = None
    weightedValue: ESCOWeightedValue | None = None


class ESCOPostAward(PostAward):
    value: ESCOValue | None = None
    weightedValue: ESCOWeightedValue | None = None
