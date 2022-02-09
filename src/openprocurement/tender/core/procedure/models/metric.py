from openprocurement.tender.core.procedure.models.period import Period
from openprocurement.api.models import Model, Value
from schematics.validate import ValidationError
from schematics.types import StringType, MD5Type
from schematics.types.compound import ListType, ModelType
from uuid import uuid4


class Unit(Model):
    name = StringType()
    id = StringType()
    scheme = StringType()
    uri = StringType()


class Dimension(Model):
    description = StringType()


class MilestoneReference(Model):
    id = MD5Type()
    title = StringType()


class PostObservation(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    value = ModelType(Value)
    description = StringType()
    period = ModelType(Period)
    measure = StringType()
    unit = ModelType(Unit)
    dimensions = ListType(ModelType(Dimension))
    notes = StringType()
    relatedImplementationMilestone = ModelType(MilestoneReference)


class Observation(PostObservation):
    id = MD5Type(required=True)


class PostMetric(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True, min_length=1)
    description = StringType()
    observations = ListType(ModelType(PostObservation))


class Metric(PostMetric):
    id = MD5Type(required=True)
    observations = ListType(ModelType(Observation))


def validate_metric_ids_uniq(metrics):
    if metrics:
        metrics_ids = [i.id for i in metrics]
        if len(metrics_ids) > len(set(metrics_ids)):
            raise ValidationError(u"Metric identifier should be uniq")


def validate_observation_ids_uniq(metrics):
    if metrics:
        obs_ids = [observation.id for metric in metrics for observation in metric.observations]
        if len(obs_ids) > len(set(obs_ids)):
            raise ValidationError(u"Observation identifier should be uniq for all observation in tender")

