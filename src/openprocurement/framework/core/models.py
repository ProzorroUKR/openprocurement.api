# -*- coding: utf-8 -*-
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist, whitelist
from schematics.types import StringType, BaseType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from zope.interface import implementer

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.interfaces import IOPContent
from openprocurement.api.models import OpenprocurementSchematicsDocument, Model
from openprocurement.api.models import (
    Revision,
    IsoDateTimeType,
    ListType,
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
        _create_role = _edit_role + whitelist("frameworkType", "submissionMethodDetails", "mode")

        roles = {
            "create": _create_role,
            "edit_draft": _edit_role,
            "view": _create_role + whitelist(
                "date",
                "prettyID",
                "documents",
                "doc_id",
                "submissionMethodDetails",
                "dateModified",
                "frameworkType",
                "owner",
            ),
            "chronograph": whitelist("status", "next_check"),
            "chronograph_view": whitelist(
                "status",
                "doc_id",
                "submissionMethodDetails",
                "mode",
            ),
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
        submissionMethodDetails = StringType()
    owner = StringType()
    owner_token = StringType()
    mode = StringType(choices=["test"])
    transfer_token = StringType()

    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    revisions = ListType(ModelType(Revision, required=True), default=list())

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
        root = self.get_root()
        request = root.request
        if request.method == "POST":
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

    def validate_submissionMethodDetails(self, *args, **kw):
        if self.mode and self.mode == "test" and self.submissionMethodDetails and self.submissionMethodDetails != "":
            raise ValidationError(u"submissionMethodDetails should be used with mode test")
