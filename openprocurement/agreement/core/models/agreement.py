# -*- coding: utf-8 -*-
from uuid import uuid4
from pyramid.security import Allow
from zope.interface import implementer, provider

from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.agreement.core.interfaces import IAgreement
from openprocurement.api.models import (
    IsoDateTimeType,
    Model,
    Period,
    Revision,
    ListType,
    OpenprocurementSchematicsDocument
    )


@implementer(IAgreement)
@provider(IAgreement)
class Agreement(OpenprocurementSchematicsDocument, Model):
    """ Base agreement model """

    agreementID = StringType()
    # maybe terminated ????
    status = StringType(
        choices=['active', 'cancelled'],
        required=True
        )
    date = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    description = StringType()
    title = StringType()
    revisions = ListType(ModelType(Revision), default=list())
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    owner_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=['test'])

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

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


    def __repr__(self):
        return '<%s:%r@%r>' % (type(self).__name__, self.id, self.rev)