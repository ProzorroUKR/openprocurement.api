# -*- coding: utf-8 -*-
from uuid import uuid4
from pyramid.security import Allow
from zope.interface import implementer

from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.agreement.core.interfaces import IAgreement
from openprocurement.agreement.core.constants import DEFAULT_TYPE
from openprocurement.api.models import (
    IsoDateTimeType,
    Model,
    Period,
    Revision,
    ListType,
    OpenprocurementSchematicsDocument
    )


@implementer(IAgreement)
class Agreement(OpenprocurementSchematicsDocument, Model):
    """ Base agreement model """

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementType = StringType(default=DEFAULT_TYPE)
    agreementID = StringType()
    agreementNumber = StringType()
    status = StringType(
        choices=['pending', 'active', 'cancelled'],
        default='pending'
        )
    date = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    description = StringType()
    period = ModelType(Period)
    title = StringType()
    revisions = ListType(ModelType(Revision), default=list())
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    owner_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=['test'])

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [
            k for k in data.keys()
            if data[k] == self.__class__.fields[k].default
               or data[k] == getattr(self, k)
        ]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self

    def __local_roles__(self):
        return dict([
            ('{}_{}'.format(self.owner, self.owner_token), 'agreement_owner'),
            ('{}_{}'.format(self.owner, self.tender_token), 'tender_owner')
            ])

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_agreement'),
            #(Allow, '{}_{}'.format(self.owner, self.tender_token), 'generate_credentials')
        ]
        return acl