import itertools
from uuid import uuid4

from pydantic import Field

from openprocurement.api.procedure.models.base import Model, validate_list_uniq_factory
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
)


class Unit(Model):
    name: str | None = None
    id: str | None = None
    scheme: str | None = None
    uri: str | None = None


class Dimension(Model):
    description: str | None = None


class MilestoneReference(Model):
    id: MD5 | None = None
    title: str | None = None


class PostObservation(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    title: str = Field(min_length=1)
    value: Value | None = None
    description: str | None = None
    period: Period | None = None
    measure: str | None = None
    unit: Unit | None = None
    dimensions: list[Dimension] | None = None
    notes: str | None = None
    relatedImplementationMilestone: MilestoneReference | None = None


class Observation(PostObservation):
    id: MD5


class PostMetric(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    title: str = Field(min_length=1)
    description: str | None = None
    observations: list[PostObservation] | None = None


class Metric(PostMetric):
    id: MD5
    observations: list[Observation] | None = None


def validate_observation_ids_uniq(metrics):
    validation_func = validate_list_uniq_factory(
        "id", err_field="observations", err_msg="All observations in tender should be unique"
    )
    validation_func(itertools.chain([x.observations for x in metrics]))
