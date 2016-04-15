# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface
from couchdb_schematics.document import SchematicsDocument
from schematics.types import StringType, BaseType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from openprocurement.api.models import Contract as BaseContract
from openprocurement.api.models import ListType, Revision, IsoDateTimeType
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, Administrator_role,
    schematics_default_role)
from openprocurement.tender.openeu.models import Document as BaseDocument


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
    owner_token = StringType()
    owner = StringType()
    mode = StringType(choices=['test'])  # XXX is it usable?

    create_accreditation = 3  # TODO

    class Options:
        roles = {  # TODO
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role,
            'view': view_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
        }

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'contract_owner')])

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
