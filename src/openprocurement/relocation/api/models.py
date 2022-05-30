from schematics.transforms import whitelist
from schematics.types import StringType
from schematics.types.serializable import serializable
from uuid import uuid4

from openprocurement.api.models import plain_role, get_now, schematics_default_role, IsoDateTimeType, RootModel


class Transfer(RootModel):
    class Options:
        roles = {
            "plain": plain_role,
            "default": schematics_default_role,
            "create": whitelist(),
            "view": whitelist("id", "doc_id", "date", "usedFor"),
        }

    owner = StringType(min_length=1)
    access_token = StringType(min_length=1, default=lambda: uuid4().hex)
    transfer_token = StringType(min_length=1, default=lambda: uuid4().hex)
    date = IsoDateTimeType(default=get_now)
    usedFor = StringType(min_length=32)  # object path (e.g. /tenders/{id})

    def __repr__(self):
        return "<%s:%r@%r>" % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name="id")
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id
