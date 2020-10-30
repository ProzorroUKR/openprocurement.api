from uuid import uuid4

from pyramid.security import Allow
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist

from openprocurement.api.utils import get_now
from openprocurement.api.models import BusinessOrganization
from openprocurement.api.models import (
    ListType, Value, IsoDateTimeType
    )
from openprocurement.tender.core.models import Model, Document
from openprocurement.tender.core.models import (
    Administrator_bid_role,
    view_bid_role,
)
from openprocurement.tender.pricequotation.validation import\
    validate_bid_value, validate_requirement_responses


class RequirementReference(Model):
    id = StringType(required=True)
    title = StringType()


class RequirementResponse(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    requirement = ModelType(RequirementReference, required=True)
    value = StringType(required=True)


class Bid(Model):
    class Options:
        roles = {
            "Administrator": Administrator_bid_role,
            "embedded": view_bid_role,
            "view": view_bid_role,
            "create": whitelist(
                "value",
                "status",
                "tenderers",
                "parameters",
                "documents",
                "requirementResponses"
            ),
            "edit": whitelist("value", "status", "tenderers"),
            "active.tendering": whitelist(),
            "active.qualification": view_bid_role,
            "active.awarded": view_bid_role,
            "complete": view_bid_role,
            "unsuccessful": view_bid_role,
            "cancelled": view_bid_role,
        }

    def __local_roles__(self):
        return dict([("{}_{}".format(self.owner, self.owner_token),
                      "bid_owner")])

    tenderers = ListType(
        ModelType(BusinessOrganization, required=True),
        required=True,
        min_size=1,
        max_size=1
    )
    date = IsoDateTimeType(default=get_now)
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["active", "draft"], default="active")
    value = ModelType(Value)
    documents = ListType(ModelType(Document, required=True), default=list())
    owner_token = StringType()
    transfer_token = StringType()
    owner = StringType()
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.

        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if k != "value" and data[k] is None]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __acl__(self):
        return [
            (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_bid")
        ]

    def validate_value(self, data, value):
        parent = data["__parent__"]
        if isinstance(parent, Model):
            validate_bid_value(parent, value)

    def validate_requirementResponses(self, data, value):
        criterion = data["__parent__"]['criteria']
        validate_requirement_responses(
            criterion, value
        )
