from schematics.types import StringType

from openprocurement.api.procedure.models.identifier import Identifier as BaseIdentifier


class Identifier(BaseIdentifier):
    legalName = StringType(required=True)


class SubmissionIdentifier(BaseIdentifier):
    legalName = StringType(required=True)
