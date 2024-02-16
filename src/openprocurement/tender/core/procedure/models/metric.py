from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.compound import ListType, ModelType
from schematics.validate import ValidationError

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import Value


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
            raise ValidationError("Metric identifier should be uniq")


def validate_observation_ids_uniq(metrics):
    if metrics:
        obs_ids = [observation.id for metric in metrics for observation in metric.observations]
        if len(obs_ids) > len(set(obs_ids)):
            raise ValidationError("Observation identifier should be uniq for all observation in tender")
