# -*- coding: utf-8 -*-
from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.types import MD5Type, IntType
from openprocurement.api.models import (
    Model,
    Period,
    IsoDateTimeType,
    ListType,
    Reference,
)
from schematics.types import StringType
from openprocurement.api.constants import (
    RELEASE_ECRITERIA_ARTICLE_17,
    CRITERION_REQUIREMENT_STATUSES_FROM,
)
from openprocurement.tender.core.procedure.validation import (
    validate_value_type,
)
from openprocurement.tender.core.procedure.context import get_tender, get_bid, get_json_data, get_now
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.models.base import (
    BaseBid,
    validate_object_id_uniq,
)
from openprocurement.tender.core.models import (
    BaseAward, QualificationMilestoneListMixin,
    validate_response_requirement_uniq,
)
from logging import getLogger

LOGGER = getLogger(__name__)


class RequirementReference(Model):
    id = StringType(required=True)
    title = StringType()


class RequirementResponse(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    requirement = ModelType(RequirementReference, required=True)
    value = StringType(required=True)

