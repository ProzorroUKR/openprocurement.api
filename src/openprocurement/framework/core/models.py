# -*- coding: utf-8 -*-
from uuid import uuid4

from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, BaseType, MD5Type
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from zope.interface import implementer

from openprocurement.api.auth import ACCR_5
from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.interfaces import IOPContent
from openprocurement.api.models import OpenprocurementSchematicsDocument, Model
from openprocurement.api.models import (
    Revision,
    IsoDateTimeType,
    ListType,
    BusinessOrganization,
    Document,
    Organization as BaseOrganization,
    ContactPoint as BaseContactPoint
)
from openprocurement.api.utils import get_now


class IFramework(IOPContent):
    """ Base framework marker interface """


@implementer(IFramework)
class Framework(OpenprocurementSchematicsDocument, Model):
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
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type", "__parent__"
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

    central_accreditations = (ACCR_5,)
    edit_accreditations = (ACCR_5,)

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


class ContactPoint(BaseContactPoint):
    def validate_telephone(self, data, value):
        pass


class Organization(BaseOrganization):
    contactPoint = ModelType(ContactPoint, required=True)
    pass


class SubmissionBusinessOrganization(BusinessOrganization):
    pass


@implementer(ISubmission)
class Submission(OpenprocurementSchematicsDocument, Model):
    class Options:
        namespace = "Submission"
        roles = {
            "create": whitelist("tenderers", "documents", "frameworkID"),
            "edit": whitelist("tenderers", "status", "frameworkID"),
            "edit_active": whitelist(),
            "edit_bot": whitelist("status", "qualificationID"),
            "default": blacklist("doc_id", "__parent__"),
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type", "__parent__"
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
            ),
            "embedded":  blacklist("_id", "_rev", "doc_type", "__parent__"),
        }

    tenderers = ListType(ModelType(SubmissionBusinessOrganization, required=True), required=True, min_size=1,)
    documents = ListType(ModelType(Document, required=True), default=list())
    qualificationID = StringType()
    frameworkID = StringType(required=True)
    dateModified = IsoDateTimeType()
    date = IsoDateTimeType(default=get_now)
    datePublished = IsoDateTimeType()

    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)

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


@implementer(IQualification)
class Qualification(OpenprocurementSchematicsDocument, Model):

    class Options:
        namespace = "Qualification"
        roles = {
            "create": whitelist("submissionID", "frameworkID", "documents"),
            "edit": whitelist("status", "documents"),
            "default": blacklist("doc_id", "__parent__"),
            "plain": blacklist(  # is used for getting patches
                "_attachments", "revisions", "dateModified", "_id", "_rev", "doc_type", "__parent__"
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
            ),
            "embedded":  blacklist("_id", "_rev", "doc_type", "__parent__"),
        }

    submissionID = StringType(required=True)
    frameworkID = StringType(required=True)

    date = IsoDateTimeType(default=get_now)
    dateModified = IsoDateTimeType()

    framework_owner = StringType()
    framework_token = StringType()

    documents = ListType(ModelType(Document, required=True), default=list())

    _attachments = DictType(DictType(BaseType), default=dict())
    revisions = BaseType(default=list)

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


@implementer(IAgreement)
class Agreement(OpenprocurementSchematicsDocument, Model):
    """ Base agreement model """

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementType = StringType(default="electronicCatalogue")
    # maybe terminated ????
    status = StringType(choices=["active", "terminated"], required=True)
    date = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    revisions = BaseType(default=list)
    owner_token = StringType(default=lambda: uuid4().hex)
    transfer_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=["test"])

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
