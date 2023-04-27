from datetime import timedelta

from uuid import uuid4
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import (
    StringType,
    BaseType,
    MD5Type,
    BooleanType,
)
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from zope.interface import implementer

from openprocurement.api.auth import (
    ACCR_1,
    ACCR_2,
    ACCR_3,
    ACCR_4,
    ACCR_5,
)
from openprocurement.api.constants import (
    SANDBOX_MODE,
    DK_CODES,
    REQUIRED_FIELDS_BY_SUBMISSION_FROM,
)
from openprocurement.api.interfaces import IOPContent
from openprocurement.api.models import (
    RootModel,
    IsoDateTimeType,
    ListType,
    Document,
    Organization as BaseOrganization,
    ContactPoint as BaseContactPoint,
    Classification as BaseClassification,
    Identifier as BaseIdentifier,
    Address as BaseAddress,
    BusinessOrganization as BaseBusinessOrganization,
    Model,
)
from openprocurement.api.utils import (
    get_now,
    required_field_from_date,
)
from openprocurement.framework.core.context import get_framework
from openprocurement.framework.core.utils import calculate_framework_date
from openprocurement.framework.dps.constants import DPS_TYPE

CONTRACT_BAN_DURATION = 90


class IFramework(IOPContent):
    """ Base framework marker interface """


class FrameworkConfig(Model):
    test = BooleanType(required=False)
    restrictedDerivatives = BooleanType(required=False)

    def validate_restrictedDerivatives(self, data, value):
        framework = get_framework()
        if not framework:
            return
        if framework.get("frameworkType") == DPS_TYPE:
            if value is None:
                raise ValidationError("restrictedDerivatives is required for this framework type")
            if framework.get("procuringEntity", {}).get("kind") == "defense":
                if value is False:
                    raise ValidationError("restrictedDerivatives must be true for defense procuring entity")
            else:
                if value is True:
                    raise ValidationError("restrictedDerivatives must be false for non-defense procuring entity")
        else:
            if value is not None:
                raise ValidationError("restrictedDerivatives not allowed for this framework type")


def get_agreement(model):
    while not IAgreement.providedBy(model):
        model = model.__parent__
    return model


@implementer(IFramework)
class Framework(RootModel):
    class Options:
        namespace = "Framework"
        _edit_role = whitelist(
            "title",
            "title_en",
            "title_ru",
            "description",
            "description_en",
            "description_ru",
        )
        _create_role = _edit_role + whitelist("frameworkType", "frameworkDetails", "mode")
        _view_role = _create_role + whitelist(
                "date",
                "prettyID",
                "documents",
                "doc_id",
                "frameworkDetails",
                "dateModified",
                "frameworkType",
                "owner",
            )
        roles = {
            # Specify for inheritance when several framework types appear
            "create": _create_role,
            "edit_draft": _edit_role,
            "view": _view_role,
            "chronograph": whitelist("next_check"),
            "chronograph_view": _view_role,
            # "Administrator": whitelist("status", "mode"),
            "default": blacklist("doc_id", "__parent__"),  # obj.store() use default role
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified",
                "_id", "_rev", "doc_type", "__parent__", "public_modified", "config"
            ),
            "listing": whitelist("dateModified", "doc_id"),
            "embedded": blacklist("_id", "_rev", "doc_type", "__parent__"),
        }

    prettyID = StringType()
    title = StringType(required=True)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    frameworkType = StringType(required=True)
    if SANDBOX_MODE:
        frameworkDetails = StringType()
    owner = StringType()
    owner_token = StringType()
    mode = StringType(choices=["test"])
    transfer_token = StringType()
    status = StringType(choices=["draft"], default="draft")

    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    revisions = BaseType(default=list)
    config = BaseType()

    create_accreditations = (ACCR_1, ACCR_3, ACCR_5)
    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_2, ACCR_4)

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "framework_owner")])
        return roles

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    @serializable(serialized_name="date")
    def old_date(self):
        if self.__parent__ is None:
            return get_now().isoformat()
        root = self.get_root()
        request = root.request
        if not self.date and request.method == "POST":
            return get_now().isoformat()
        return self.date.isoformat()

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        elif request.authenticated_role == "chronograph":
            role = "chronograph"
        else:
            role = "edit_{}".format(request.context.status)
        return role

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_framework"),
        ]
        return acl

    def validate_frameworkDetails(self, *args, **kw):
        if self.mode and self.mode == "test" and self.frameworkDetails and self.frameworkDetails != "":
            raise ValidationError("frameworkDetails should be used with mode test")


class ISubmission(IOPContent):
    pass


class SubmissionConfig(Model):
    test = BooleanType(required=False)
    restricted = BooleanType(required=False)

    def validate_restricted(self, data, value):
        framework = get_framework()
        if not framework:
            return
        if framework.get("frameworkType") == DPS_TYPE:
            if value is None:
                raise ValidationError("restricted is required for this framework type")
            if framework.get("procuringEntity", {}).get("kind") == "defense":
                if value is False:
                    raise ValidationError("restricted must be true for defense procuring entity")
            else:
                if value is True:
                    raise ValidationError("restricted must be false for non-defense procuring entity")
        else:
            if value is not None:
                raise ValidationError("restricted not allowed for this framework type")


class ContactPoint(BaseContactPoint):
    def validate_telephone(self, data, value):
        pass


class Organization(BaseOrganization):
    contactPoint = ModelType(ContactPoint, required=True)


class SubmissionAddress(BaseAddress):

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
    identifier = ModelType(SubmissionIdentifier, required=True)
    address = ModelType(SubmissionAddress, required=True)
    contactPoint = ModelType(SubmissionContactPoint, required=True)

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_name(self, data, value):
        return value


class SubmissionBusinessOrganization(SubmissionOrganization, BaseBusinessOrganization):
    pass


@implementer(ISubmission)
class Submission(RootModel):
    class Options:
        namespace = "Submission"
        roles = {
            "create": whitelist("tenderers", "documents", "frameworkID"),
            "edit": whitelist("tenderers", "status", "frameworkID"),
            "edit_active": whitelist(),
            "edit_bot": whitelist("status", "qualificationID"),
            "default": blacklist("doc_id", "__parent__"),
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev",
                "doc_type", "__parent__", "public_modified", "config",
            ),
            "view": whitelist(
                "doc_id",
                "owner",
                "status",
                "tenderers",
                "documents",
                "qualificationID",
                "frameworkID",
                "dateModified",
                "date",
                "datePublished",
                "submissionType",
                "mode",
            ),
            "embedded":  blacklist("_id", "_rev", "doc_type", "__parent__"),
        }

    tenderers = ListType(ModelType(SubmissionBusinessOrganization, required=True), required=True, min_size=1, )
    documents = ListType(ModelType(Document, required=True), default=list())
    qualificationID = StringType()
    frameworkID = StringType(required=True)
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType(default=get_now)
    datePublished = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()

    framework_owner = StringType()
    framework_token = StringType()

    transfer_token = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])

    def get_role(self):
        role = "edit"
        root = self.__parent__
        auth_role = root.request.authenticated_role
        if auth_role == "bots":
            role = "edit_bot"
        elif self.status == "active":
            role = "edit_active"
        return role

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "submission_owner")])
        return roles

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_submission"),
        ]
        return acl


class IQualification(IOPContent):
    pass


class QualificationConfig(Model):
    test = BooleanType(required=False)


@implementer(IQualification)
class Qualification(RootModel):

    class Options:
        namespace = "Qualification"
        roles = {
            "create": whitelist("submissionID", "frameworkID", "documents"),
            "edit": whitelist("status", "documents"),
            "default": blacklist("doc_id", "__parent__"),
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev",
                "doc_type", "__parent__", "public_modified", "config",
            ),
            "view": whitelist(
                "doc_id",
                "status",
                "submissionID",
                "frameworkID",
                "documents",
                "date",
                "dateModified",
                "qualificationType",
                "mode",
            ),
            "embedded":  blacklist("_id", "_rev", "doc_type", "__parent__"),
        }

    submissionID = StringType(required=True)
    frameworkID = StringType(required=True)

    date = IsoDateTimeType(default=get_now)
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()

    framework_owner = StringType()
    framework_token = StringType()

    submission_owner = StringType()
    submission_token = StringType()

    documents = ListType(ModelType(Document, required=True), default=list())

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)
    config = BaseType()

    mode = StringType(choices=["test"])

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.framework_owner, self.framework_token), "edit_qualification"),
        ]
        return acl


class IAgreement(IOPContent):
    """ Base interface for agreement container """


class AgreementConfig(Model):
    test = BooleanType(required=False)


@implementer(IAgreement)
class Agreement(RootModel):
    """ Base agreement model """

    # id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementType = StringType(required=True)
    # maybe terminated ????
    status = StringType(choices=["active", "terminated"], required=True)
    date = IsoDateTimeType()
    dateCreated = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    revisions = BaseType(default=list)
    owner_token = StringType(default=lambda: uuid4().hex)
    transfer_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=["test"])
    config = BaseType()

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __local_roles__(self):
        return dict(
            [
                ("{}_{}".format(self.owner, self.owner_token), "agreement_owner"),
            ]
        )

    def __acl__(self):
        acl = [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_agreement"),
        ]
        return acl

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)


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


class ContractContactPoint(BaseContactPoint):
    pass


class ContractOrganization(BaseOrganization):
    contactPoint = ModelType(ContractContactPoint, required=True)


class ContractBusinessOrganization(ContractOrganization, BaseBusinessOrganization):
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
    suppliers = ListType(ModelType(ContractBusinessOrganization, required=True), required=True, min_size=1, )
    milestones = ListType(ModelType(Milestone, required=True), required=True, min_size=1, )
    date = IsoDateTimeType(default=get_now)

    def validate_suppliers(self, data, suppliers):
        if len(suppliers) != 1:
            raise ValidationError("Contract must have only one supplier")
