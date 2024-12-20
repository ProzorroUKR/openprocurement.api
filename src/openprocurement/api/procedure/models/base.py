from schematics.models import Model as SchematicsModel
from schematics.types import BaseType, StringType
from schematics.types.serializable import serializable


class Model(SchematicsModel):
    class Options:
        """Export options for Document."""

        serialize_when_none = False

    def __getitem__(self, name):
        try:
            return getattr(self, name)
        except AttributeError as e:
            raise KeyError(e)


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
