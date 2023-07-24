import re
from enum import Enum
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, StringType, URLType, MD5Type
from schematics.types.compound import ListType, ModelType
from schematics.types.serializable import serializable

from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.models.complaint_objection_argument import Argument
from openprocurement.tender.core.procedure.models.complaint_objection_requested_remedy import RequestedRemedy


class ObjectionRelatesTo(Enum):
    tender = "tender"
    lot = "lot"
    requirement = "requirement"
    requirement_response = "requirementResponse"
    award = "award"
    qualification = "qualification"
    cancellation = "cancellation"


OBJECTION_RELATES_REGEX_MAPPING = {
    ObjectionRelatesTo.tender: r"^tenders\/(?P<tender_id>[0-9a-fA-F]{32})$",
    ObjectionRelatesTo.lot: (
        r"^"
        r"tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"lots\/(?P<lot_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.requirement: (
        r"^"
        r"tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"criteria\/(?P<criterion_id>[0-9a-fA-F]{32})"
        r"\/"
        r"requirementGroups\/(?P<requirement_group_id>[0-9a-fA-F]{32})"
        r"\/"
        r"requirements\/(?P<requirement_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.requirement_response: (
        r"^"
        r"tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"("
        r"bids\/(?P<bid_id>[0-9a-fA-F]{32})"
        r"|"
        r"awards\/(?P<award_id>[0-9a-fA-F]{32})"
        r"|"
        r"qualifications\/(?P<qualification_id>[0-9a-fA-F]{32})"
        r")"
        r"\/"
        r"requirementResponses\/(?P<requirement_response_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.award: (
        r"^"
        r"tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"awards\/(?P<award_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.qualification: (
        r"^"
        r"tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"qualifications\/(?P<qualification_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.cancellation: (
        r"^"
        r"tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"cancellations\/(?P<cancellation_id>[0-9a-fA-F]{32})"
        r"$"
    ),
}


class Classification(Model):
    scheme = StringType(required=True)
    id = StringType(required=True)
    description = StringType(required=True)
    uri = URLType()


class Objection(Model):
    @serializable
    def id(self):
        return uuid4().hex

    title = StringType(required=True)
    description = StringType(required=True)
    relatesTo = StringType(choices=[choice.value for choice in ObjectionRelatesTo], required=True)
    relatedItem = StringType(required=True)
    classification = ModelType(Classification, required=True)
    requestedRemedies = ListType(ModelType(RequestedRemedy), min_size=1, required=True)
    arguments = ListType(ModelType(Argument), min_size=1, required=True)

    def validate_relatedItem(self, data, value):
        relates_to = data["relatesTo"]
        related_regex = OBJECTION_RELATES_REGEX_MAPPING[getattr(ObjectionRelatesTo, relates_to)]
        related_re = re.compile(related_regex, re.IGNORECASE)
        related_match = related_re.search(value)
        if not related_match:
            raise ValidationError("Invalid relatedItem pattern")
        return related_match.groupdict()
