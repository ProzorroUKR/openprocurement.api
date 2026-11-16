from openprocurement.api.procedure.models.identifier import Identifier as BaseIdentifier


class Identifier(BaseIdentifier):
    legalName: str


class SubmissionIdentifier(BaseIdentifier):
    legalName: str
