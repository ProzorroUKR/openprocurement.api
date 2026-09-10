from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.award import Award, PostAward
from openprocurement.tender.esco.procedure.models.value import ESCOValue, ESCOWeightedValue


class ESCOAward(Award):
    value = ModelType(ESCOValue)
    weightedValue = ModelType(ESCOWeightedValue)


class ESCOPostAward(PostAward):
    value = ModelType(ESCOValue)
    weightedValue = ModelType(ESCOWeightedValue)
