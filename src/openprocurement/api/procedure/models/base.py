from schematics.models import Model as SchematicsModel
from schematics.transforms import blacklist, convert, export_loop
from schematics.types import BaseType, StringType
from schematics.types.serializable import serializable

from openprocurement.api.utils import set_parent


class Model(SchematicsModel):
    class Options:
        """Export options for Document."""

        serialize_when_none = False
        roles = {
            "default": blacklist("__parent__"),
            "embedded": blacklist("__parent__"),
        }

    __parent__ = BaseType()

    def __getitem__(self, name):
        try:
            return getattr(self, name)
        except AttributeError as e:
            raise KeyError(e)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            for k in self._fields:
                if k != "__parent__" and self.get(k) != other.get(k):
                    return False
            return True
        return NotImplemented

    def convert(self, raw_data, **kw):
        """
        Converts the raw data into richer Python constructs according to the
        fields on the model
        """
        value = convert(self.__class__, raw_data, **kw)
        for i, j in value.items():
            if isinstance(j, list):
                for x in j:
                    set_parent(x, self)
            else:
                set_parent(j, self)
        return value

    def to_patch(self, role=None):
        """
        Return data as it would be validated. No filtering of output unless
        role is defined.
        """

        def field_converter(field, value):
            return field.to_primitive(value)

        data = export_loop(
            self.__class__,
            self,
            field_converter,
            role=role,
            raise_error_on_role=True,
            print_none=True,
        )
        return data

    def get_role(self):
        root = self.get_root()
        request = root.request
        return "Administrator" if request.authenticated_role == "Administrator" else "edit"

    def get_root(self):
        root = self.__parent__
        while root.__parent__ is not None:
            root = root.__parent__
        return root


class RootModel(Model):
    _id = StringType(deserialize_from=["id", "doc_id"])
    _rev = StringType()
    doc_type = StringType()
    public_modified = BaseType()
    public_ts = BaseType()

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def _get_id(self):
        """id property getter."""
        return self._id

    def _set_id(self, value):
        """id property setter."""
        if self.id is not None:
            raise AttributeError("id can only be set on new documents")
        self._id = value

    id = property(_get_id, _set_id, doc="The document ID")

    @property
    def rev(self):
        """A property for self._rev"""
        return self._rev
