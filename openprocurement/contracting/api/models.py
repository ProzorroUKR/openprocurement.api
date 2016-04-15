# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface
from couchdb_schematics.document import SchematicsDocument
from schematics.types import StringType, BaseType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from openprocurement.api.models import Contract as BaseContract
from openprocurement.api.models import ListType, Revision, IsoDateTimeType
from openprocurement.api.models import (plain_role, Administrator_role,
                                        schematics_default_role)
from openprocurement.tender.openeu.models import Document as BaseDocument

contract_create_role = (whitelist(
    'id', 'awardID', 'contractID', 'contractNumber', 'title', 'title_en',
    'title_ru', 'description', 'description_en', 'description_ru', 'status',
    'period', 'value', 'dateSigned', 'documents', 'items', 'suppliers',
    'owner', 'owner_token', 'tender_token', 'mode'
))

contract_edit_role = (whitelist(
    'title', 'title_en', 'title_ru', 'description', 'description_en',
    'description_ru', 'status', 'period', 'value' , 'mode'
))

contract_view_role = (whitelist(
    'id', 'awardID', 'contractID', 'dateModified', 'contractNumber', 'title',
    'title_en', 'title_ru', 'description', 'description_en', 'description_ru',
    'status', 'period', 'value', 'dateSigned', 'documents', 'items',
    'suppliers', 'owner', 'mode'
))


class IContract(Interface):
    """ Contract marker interface """


class Document(BaseDocument):
    """ Contract Document """


@implementer(IContract)
class Contract(SchematicsDocument, BaseContract):
    """ Contract """

    revisions = ListType(ModelType(Revision), default=list())
    dateModified = IsoDateTimeType()
    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    tender_token = StringType()
    owner_token = StringType()
    owner = StringType()
    mode = StringType(choices=['test'])  # XXX is it usable?

    create_accreditation = 3  # TODO

    class Options:
        roles = {  # TODO
            'plain': plain_role,
            'create': contract_create_role,
            'edit': contract_edit_role,
            'view': contract_view_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
        }

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'contract_owner'),
                     ('{}_{}'.format(self.owner, self.tender_token), 'tender_owner')])

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
