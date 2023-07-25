from enum import Enum
from uuid import uuid4

from schematics.types import StringType, MD5Type

from openprocurement.api.models import Model


class RequestedRemedyType(Enum):
    set_aside = "setAside"
    change_tender_documentation = "changeTenderDocumentation"
    provide_clarification = "provideClarification"
    tender_cancellation = "tenderCancellation"
    set_aside_reject = "setAsideReject"
    set_aside_qualification = "setAsideQualification"
    set_aside_award = "setAsideAward"
    set_aside_others = "setAsideOthers"


class RequestedRemedy(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    type = StringType(choices=[choice.value for choice in RequestedRemedyType], required=True)
    description = StringType(required=True)
