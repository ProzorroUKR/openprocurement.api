# -*- coding: utf-8 -*-
from hashlib import md5
from uuid import uuid4
from zope.interface import implementer, Interface
from couchdb_schematics.document import SchematicsDocument
from pyramid.security import Allow
from schematics.types import StringType, BaseType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from openprocurement.api.models import Contract as BaseContract
from openprocurement.api.models import Document as BaseDocument
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import ListType, Revision, IsoDateTimeType
from openprocurement.api.models import (plain_role, Administrator_role,
                                        schematics_default_role)

contract_create_role = (whitelist(
    'id', 'awardID', 'contractID', 'contractNumber', 'title', 'title_en',
    'title_ru', 'description', 'description_en', 'description_ru', 'status',
    'period', 'value', 'dateSigned', 'documents', 'items', 'suppliers',
    'owner', 'tender_token', 'tender_id', 'mode'
))

contract_edit_role = (whitelist(
    'title', 'title_en', 'title_ru', 'description', 'description_en',
    'description_ru', 'status', 'period', 'value' , 'mode'
))

contract_view_role = (whitelist(
    'id', 'awardID', 'contractID', 'dateModified', 'contractNumber', 'title',
    'title_en', 'title_ru', 'description', 'description_en', 'description_ru',
    'status', 'period', 'value', 'dateSigned', 'documents', 'items',
    'suppliers', 'owner', 'mode', 'tender_id'
))


class IContract(Interface):
    """ Contract marker interface """


class Document(BaseDocument):
    """ Contract Document """


class Item(BaseItem):
    def validate_relatedLot(self, data, relatedLot):
        pass


@implementer(IContract)
class Contract(SchematicsDocument, BaseContract):
    """ Contract """

    revisions = ListType(ModelType(Revision), default=list())
    dateModified = IsoDateTimeType()
    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    items = ListType(ModelType(Item))
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    owner_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=['test'])

    create_accreditation = 3  # TODO

    class Options:
        roles = {  # TODO
            'plain': plain_role,
            'create': contract_create_role,
            'edit_draft': whitelist("status"),
            'edit_active': contract_edit_role,
            'view': contract_view_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
        }

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'contract_owner'),
                     ('{}_{}'.format(self.owner, self.tender_token), 'tender_owner')])

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_contract'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_contract_documents'),
            (Allow, '{}_{}'.format(self.owner, self.tender_token), 'generate_credentials')
        ]
        return acl

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def validate_status(self, data, status):
        if status == 'pending':
            raise ValidationError(u"'pending' contracts are not allowed.")
    def validate_awardID(self, data, awardID):
        pass
    def validate_dateSigned(self, data, value):
        pass
