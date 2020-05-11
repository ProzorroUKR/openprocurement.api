# -*- coding: utf-8 -*-
import jmespath
from openprocurement.api.roles import RolesFromCsv
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types import StringType
from openprocurement.tender.core.models import ContractValue
from openprocurement.tender.core.utils import get_contract_supplier_roles,  get_contract_supplier_permissions, flatten_multidimensional_list, get_all_nested_from_the_object
from openprocurement.api.utils import get_now
from openprocurement.api.models import Model, ListType, Contract as BaseContract, Document
from openprocurement.tender.core.models import get_tender


class ContractDocument(Document):
    documentOf = StringType(required=True, choices=["tender","document"], default="tender")

    def validate_relatedItem(self, data, relatedItem):
        if not relatedItem and data.get("documentOf") in ["document"]:
            raise ValidationError(u"This field is required.")
        parent = data["__parent__"]
        tender = get_tender(parent)
        if data.get("documentOf") == "document":
            documents = get_all_nested_from_the_object("documents",tender) + get_all_nested_from_the_object("documents",parent)
            if relatedItem not in [i.id for i in documents]:
                raise ValidationError(u"relatedItem should be one of documents")


class Contract(BaseContract):
    class Options:
        roles = RolesFromCsv("Contract.csv", relative_to=__file__)

    value = ModelType(ContractValue)
    awardID = StringType(required=True)
    documents = ListType(ModelType(ContractDocument, required=True), default=list())

    def __acl__(self):
        return get_contract_supplier_permissions(self)

    def get_role(self):
        root = self.get_root()
        request = root.request
        if request.authenticated_role in ("tender_owner", "contract_supplier"):
            role = "edit_{}".format(request.authenticated_role)
        else:
            role = request.authenticated_role
        return role

    def __local_roles__(self):
        roles = {}
        roles.update(get_contract_supplier_roles(self))
        return roles

    def validate_awardID(self, data, awardID):
        parent = data["__parent__"]
        if awardID and isinstance(parent, Model) and awardID not in [i.id for i in parent.awards]:
            raise ValidationError(u"awardID should be one of awards")

    def validate_dateSigned(self, data, value):
        parent = data["__parent__"]
        if value and isinstance(parent, Model) and value > get_now():
            raise ValidationError(u"Contract signature date can't be in the future")
