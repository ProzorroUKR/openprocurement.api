# -*- coding: utf-8 -*-
from uuid import uuid4

from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, BaseType, EmailType, BooleanType, MD5Type
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.auth import ACCR_5
from openprocurement.api.constants import DK_CODES
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
    BusinessOrganization,
    IsoDateTimeType,
)
from openprocurement.api.models import Model
from openprocurement.api.utils import get_now
from openprocurement.framework.core.models import (
    Framework as BaseFramework,
    Submission as BaseSubmission,
    Qualification as BaseQualification,
    Agreement as BaseAgreement,
)
from openprocurement.framework.electroniccatalogue.utils import (
    AUTHORIZED_CPB,
    get_framework_unsuccessful_status_check_date,
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


class Milestone(Model):

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    type = StringType(required=True, choices=["activation", "ban", "disqualification"])
    dueDate = IsoDateTimeType()
    documents = ListType(ModelType(Document, required=True), default=list())
    dateModified = IsoDateTimeType(default=get_now)


class Contract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    qualificationID = StringType()
    status = StringType(choices=["active", "banned", "unsuccessful", "terminated"])
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1,)
    milestones = ListType(ModelType(Milestone, required=True), required=True, min_size=1,)
    date = IsoDateTimeType(default=get_now)


class Agreement(BaseAgreement):
    class Options:
        roles = {
            "view": blacklist("doc_type", "transfer_token", "owner_token", "revisions", "_id", "_rev", "__parent__",),
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type", "__parent__"
            ),
            "default": blacklist("doc_id", "__parent__"),  # obj.store() use default role
        }

    agreementType = StringType(default="electronicCatalogue")
    frameworkID = StringType()
    period = ModelType(BasePeriodEndRequired)
    procuringEntity = ModelType(CentralProcuringEntity, required=True)
    classification = ModelType(DKClassification, required=True)
    additionalClassifications = ListType(ModelType(BaseClassification))
    contracts = ListType(ModelType(Contract, required=True), default=list())

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    @serializable(serialize_when_none=False)
    def next_check(self):
        checks = []
        if self.status == "active":
            milestone_dueDates = [
                milestone.dueDate for contract in self.contracts for milestone in contract.milestones if milestone.dueDate
            ]
            if milestone_dueDates:
                checks.append(min(milestone_dueDates))
            checks.append(self.period.endDate)
        return min(checks).isoformat() if checks else None
