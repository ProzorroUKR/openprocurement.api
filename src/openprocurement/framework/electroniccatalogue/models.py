# -*- coding: utf-8 -*-
from datetime import timedelta
from uuid import uuid4

from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, BaseType, EmailType, BooleanType, MD5Type
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable

from openprocurement.api.auth import ACCR_5
from openprocurement.api.constants import DK_CODES, REQUIRED_FIELDS_BY_SUBMISSION_FROM
from openprocurement.api.models import (
    Document,
    ListType,
    Classification as BaseClassification,
    PeriodEndRequired as BasePeriodEndRequired,
    Identifier as BaseIdentifier,
    Address as BaseAddress,
    ContactPoint as BaseContactPoint,
    schematics_embedded_role,
    schematics_default_role,
    BusinessOrganization as BaseBusinessOrganization,
    IsoDateTimeType,
    Organization as BaseOrganization,
)
from openprocurement.api.models import Model
from openprocurement.api.utils import get_now, required_field_from_date
from openprocurement.framework.core.models import (
    Framework as BaseFramework,
    Submission as BaseSubmission,
    Qualification as BaseQualification,
    Agreement as BaseAgreement,
)
from openprocurement.framework.electroniccatalogue.utils import (
    AUTHORIZED_CPB,
    get_framework_unsuccessful_status_check_date,
    calculate_framework_date,
    CONTRACT_BAN_DURATION,
)


class DKClassification(BaseClassification):
    scheme = StringType(required=True, choices=["ДК021"])
    id = StringType(required=True)

    def validate_id(self, data, id):
        if id not in DK_CODES:
            raise ValidationError(BaseType.MESSAGES["choices"].format(DK_CODES))


class Identifier(BaseIdentifier):
    legalName = StringType(required=True)


class Address(BaseAddress):
    streetAddress = StringType(required=True)
    locality = StringType(required=True)
    region = StringType(required=True)
    postalCode = StringType(required=True)


class ContactPoint(BaseContactPoint):
    email = EmailType(required=True)
    telephone = StringType(required=True)


class CentralProcuringEntity(Model):
    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "edit_draft": schematics_default_role,
            "edit_active": whitelist("contactPoint"),
        }

    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    kind = StringType(choices=["central"], default="central")

    def validate_identifier(self, data, identifier):
        id_ = identifier.id
        cpb_with_statuses = {cpb["identifier"]["id"]: cpb["active"] for cpb in AUTHORIZED_CPB}
        if id_ not in cpb_with_statuses or not cpb_with_statuses[id_]:
            raise ValidationError("Can't create framework for inactive cpb")

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_kind(self, data, value):
        return value


class Framework(BaseFramework):
    class Options:
        _status_view_role = blacklist(
            "doc_type",
            "successful",
            "transfer_token",
            "owner_token",
            "revisions",
            "_id",
            "_rev",
            "__parent__",
        )
        _edit_role = _status_view_role + blacklist(
            "frameworkType",
            "prettyID",
            "period",
            "enquiryPeriod",
            "dateModified",
            "date",
            "doc_id"
        )
        _create_role = _edit_role + blacklist("status")

        roles = {
            "create": _create_role,
            "edit_draft": _edit_role + blacklist("owner", "old_date"),
            "edit_active": whitelist(
                "status",
                "procuringEntity",
                "qualificationPeriod",
                "description",
                "description_en",
                "description_ru",
                "documents",
                "frameworkDetails"
            ),
            "draft": _status_view_role,
            "active": _status_view_role,
            "complete": _status_view_role,
            "unsuccessful": _status_view_role,
            "view": _edit_role + whitelist(
                "date",
                "period",
                "enquiryPeriod",
                "prettyID",
                "documents",
                "doc_id",
                "dateModified",
                "status",
                "owner",
                "next_check",
            ),
            "chronograph": whitelist("next_check"),
            "chronograph_view": _status_view_role,
            "Administrator": whitelist("status", "mode"),
            "default": blacklist("doc_id", "__parent__"),  # obj.store() use default role
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type",
                "__parent__"
            ),
            "listing": whitelist("dateModified", "doc_id"),
            "embedded": blacklist("_id", "_rev", "doc_type", "__parent__"),
        }

    status = StringType(
        choices=[
            "draft",
            "active",
            "deleted",
            "complete",
            "unsuccessful",
        ],
        default="draft",
    )
    period = ModelType(BasePeriodEndRequired)
    qualificationPeriod = ModelType(BasePeriodEndRequired, required=True)
    enquiryPeriod = ModelType(BasePeriodEndRequired)
    frameworkType = StringType(default="electronicCatalogue")
    procuringEntity = ModelType(CentralProcuringEntity, required=True)
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    documents = ListType(ModelType(Document, required=True), default=list())
    agreementID = StringType()

    successful = BooleanType(required=True, default=False)

    procuring_entity_kinds = ["central"]
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_5,)

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        if self.status == "active":
            if not self.successful:
                unsuccessful_status_check = get_framework_unsuccessful_status_check_date(self)
                if unsuccessful_status_check:
                    checks.append(unsuccessful_status_check)
            checks.append(self.qualificationPeriod.endDate)
        return min(checks).isoformat() if checks else None

    def __acl__(self):
        acl = super(Framework, self).__acl__()
        acl.append((Allow, "{}_{}".format(self.owner, self.owner_token), "upload_framework_documents"))
        return acl


class AddressForSubmission(BaseAddress):

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_region(self, data, value):
        super().validate_region(self, data, value)
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_postalCode(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_locality(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_streetAddress(self, data, value):
        return value


class IdentifierForSubmission(BaseIdentifier):

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_legalName(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_id(self, data, value):
        return value


class ContactPointForSubmission(BaseContactPoint):

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_name(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_email(self, data, value):
        super().validate_email(self, data, value)
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_telephone(self, data, value):
        super().validate_telephone(self, data, value)
        return value


class OrganizationForSubmission(BaseOrganization):
    identifier = ModelType(IdentifierForSubmission, required=True)
    address = ModelType(AddressForSubmission, required=True)
    contactPoint = ModelType(ContactPointForSubmission, required=True)

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_name(self, data, value):
        return value


class BusinessOrganizationForSubmission(OrganizationForSubmission, BaseBusinessOrganization):
    pass


class Submission(BaseSubmission):
    status = StringType(
        choices=[
            "draft",
            "active",
            "deleted",
            "complete"
        ],
        default="draft",
    )
    submissionType = StringType(default="electronicCatalogue")
    tenderers = ListType(ModelType(BusinessOrganizationForSubmission, required=True), required=True, min_size=1,)


class Qualification(BaseQualification):
    status = StringType(
        choices=[
            "pending",
            "active",
            "unsuccessful"
        ],
        default="pending",
    )

    qualificationType = StringType(default="electronicCatalogue", required=True)


class BusinessOrganization(BaseBusinessOrganization):
    class Options:
        roles = {
            "edit": whitelist("contactPoint", "address"),
            "view": blacklist("doc_type", "_id", "_rev", "__parent__"),
        }


class Milestone(Model):
    class Options:
        roles = {
            "create": whitelist("type", "documents"),
            "edit": whitelist("status", "documents"),
            "view": blacklist("doc_type", "_id", "_rev", "__parent__"),
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    type = StringType(required=True, choices=["activation", "ban"])
    status = StringType(choices=["scheduled", "met", "notMet", "partiallyMet"], default="scheduled")
    dueDate = IsoDateTimeType()
    documents = ListType(ModelType(Document, required=True), default=list())
    dateModified = IsoDateTimeType(default=get_now)
    dateMet = IsoDateTimeType()

    @serializable(serialized_name="dueDate", serialize_when_none=False)
    def milestone_dueDate(self):
        if self.type == "ban" and not self.dueDate:
            request = self.get_root().request
            agreement = request.validated["agreement_src"]
            dueDate = calculate_framework_date(get_now(), timedelta(days=CONTRACT_BAN_DURATION), agreement, ceil=True)
            return dueDate.isoformat()
        return self.dueDate.isoformat() if self.dueDate else None


class Contract(Model):
    class Options:
        roles = {
            "edit": whitelist("suppliers"),
            "view": blacklist("doc_type", "_id", "_rev", "__parent__")
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    qualificationID = StringType()
    status = StringType(choices=["active", "suspended", "terminated"])
    submissionID = StringType()
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, )
    milestones = ListType(ModelType(Milestone, required=True), required=True, min_size=1, )
    date = IsoDateTimeType(default=get_now)

    def validate_suppliers(self, data, suppliers):
        if len(suppliers) != 1:
            raise ValidationError("Contract must have only one supplier")


class Agreement(BaseAgreement):
    class Options:
        _view_role = blacklist(
            "doc_type",
            "transfer_token",
            "owner_token",
            "revisions", "_id",
            "_rev",
            "__parent__",
            "frameworkDetails",
        )
        roles = {
            "edit": whitelist("status"),
            "view": _view_role,
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type", "__parent__"
            ),
            "default": blacklist("doc_id", "__parent__"),  # obj.store() use default role
            "chronograph": whitelist("next_check"),
        }

    agreementType = StringType(default="electronicCatalogue")
    frameworkID = StringType()
    period = ModelType(BasePeriodEndRequired)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    contracts = ListType(ModelType(Contract, required=True), default=list())
    frameworkDetails = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        if self.status == "active":
            milestone_dueDates = [
                milestone.dueDate
                for contract in self.contracts for milestone in contract.milestones
                if milestone.dueDate and milestone.status == "scheduled"
            ]
            if milestone_dueDates:
                checks.append(min(milestone_dueDates))
            checks.append(self.period.endDate)
        return min(checks).isoformat() if checks else None

    def __acl__(self):
        acl = super().__acl__()
        acl.append((Allow, "{}_{}".format(self.owner, self.owner_token), "upload_milestone_documents"), )
        return acl
