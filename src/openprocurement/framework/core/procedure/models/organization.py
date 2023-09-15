from schematics.types import StringType

from openprocurement.api.constants import REQUIRED_FIELDS_BY_SUBMISSION_FROM, SCALE_CODES
from openprocurement.api.models import (
    BusinessOrganization as BaseBusinessOrganization,
    ContactPoint as BaseContactPoint,
    Identifier as BaseIdentifier,
    Organization as BaseOrganization,
    ModelType,
    Model,
)
from openprocurement.framework.core.procedure.models.address import SubmissionAddress, CoreAddress as Address
from openprocurement.framework.core.procedure.utils import required_field_from_date


class ContactPoint(BaseContactPoint):
    def validate_telephone(self, data, value):
        pass


class Organization(BaseOrganization):
    contactPoint = ModelType(ContactPoint, required=True)
    address = ModelType(Address, required=True)


class Identifier(BaseIdentifier):
    legalName = StringType(required=True)


class SubmissionIdentifier(BaseIdentifier):

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_legalName(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_id(self, data, value):
        return value


class SubmissionContactPoint(BaseContactPoint):

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_name(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_email(self, data, value):
        super().validate_email(self, data, value)
        return value


class SubmissionOrganization(BaseOrganization):
    identifier = ModelType(SubmissionIdentifier)
    address = ModelType(SubmissionAddress)
    contactPoint = ModelType(SubmissionContactPoint)
    scale = StringType(choices=SCALE_CODES)


class PostSubmissionOrganization(BaseOrganization):
    identifier = ModelType(SubmissionIdentifier, required=True)
    address = ModelType(SubmissionAddress, required=True)
    contactPoint = ModelType(SubmissionContactPoint, required=True)

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_name(self, data, value):
        return value


class SubmissionBusinessOrganization(SubmissionOrganization):
    pass


class PostSubmissionBusinessOrganization(PostSubmissionOrganization, BaseBusinessOrganization):
    pass


class ContractOrganization(BaseOrganization):
    contactPoint = ModelType(BaseContactPoint, required=True)
    address = ModelType(Address, required=True)


class ContractBusinessOrganization(ContractOrganization, BaseBusinessOrganization):
    pass


class PatchContractBusinessOrganization(Model):
    contactPoint = ModelType(BaseContactPoint)
    address = ModelType(Address, required=True)
