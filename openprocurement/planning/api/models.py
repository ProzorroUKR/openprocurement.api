# -*- coding: utf-8 -*-
from uuid import uuid4

from couchdb_schematics.document import SchematicsDocument

from openprocurement.api.models import Model, Period, Revision
from openprocurement.api.models import Unit, CPVClassification, Classification, Identifier
from openprocurement.api.models import schematics_embedded_role, schematics_default_role, IsoDateTimeType, ListType
from openprocurement.api.models import validate_cpv_group, validate_items_uniq, validate_dkpp
from pyramid.security import Allow
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, IntType, FloatType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer, Interface


class IPlan(Interface):
    """ Base plan marker interface """


class Project(Model):
    """A project """
    id = StringType(required=True)
    name = StringType(required=True)


class Budget(Model):
    """A budget model """
    id = StringType(required=True)
    description = StringType(required=True)
    amount = FloatType(required=True)
    currency = StringType(required=False, default=u'UAH', max_length=3,
                          min_length=3)  # The currency in 3-letter ISO 4217 format.
    amountNet = FloatType()
    project = ModelType(Project)


class PlanItem(Model):
    """Simple item model for planing"""
    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification), default=list(), required=True, min_size=1,
                                         validators=[validate_dkpp])
    unit = ModelType(Unit)  # Description of the unit which the good comes in e.g. hours, kilograms
    quantity = IntType()  # The number of units required
    deliveryDate = ModelType(Period)
    description = StringType(required=True)  # A description of the goods, services to be provided.


class PlanOrganization(Model):
    """An organization"""
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)


class PlanTender(Model):
    """Tender for planning model """
    procurementMethod = StringType(choices=['open'], default='open', required=True)
    tenderPeriod = ModelType(Period, required=True)


# roles
plain_role = (blacklist('revisions', 'dateModified') + schematics_embedded_role)
create_role = (blacklist('owner_token', 'owner', 'revisions') + schematics_embedded_role)
edit_role = (
    blacklist('owner_token', 'owner', 'revisions', 'dateModified', 'doc_id', 'planID') + schematics_embedded_role)
view_role = (blacklist('owner', 'owner_token', '_attachments', 'revisions') + schematics_embedded_role)
listing_role = whitelist('dateModified', 'doc_id')
Administrator_role = whitelist('status', 'mode', 'procuringEntity')


@implementer(IPlan)
class Plan(SchematicsDocument, Model):
    """Plan model"""

    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role,
            'view': view_role,
            'listing': listing_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
        }

    def __local_roles__(self):
        return dict([('{}_{}'.format(self.owner, self.owner_token), 'plan_owner')])

    # fields

    # procuringEntity:identifier:scheme *
    # procuringEntity:identifier:id *
    # procuringEntity:name *
    # procuringEntity:identifier:legalName *
    procuringEntity = ModelType(PlanOrganization, required=True)

    # tender:tenderPeriod:startDate *
    # tender:procurementMethod *
    tender = ModelType(PlanTender, required=True)

    # budget:project:name
    # budget:project:id
    # budget:id *
    # budget:description *
    # budget:currency
    # budget:amount *
    # budget:amountNet
    budget = ModelType(Budget, required=True)

    # classification:scheme *
    # classification:id *
    # classification:description *
    classification = ModelType(CPVClassification, required=True)

    # additionalClassifications[0]:scheme
    # additionalClassifications[0]:id
    # additionalClassifications[0]:description
    additionalClassifications = ListType(ModelType(Classification), default=list(), required=False)

    planID = StringType()
    mode = StringType(choices=['test'])  # flag for test data ?
    items = ListType(ModelType(PlanItem), required=False, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])
    dateModified = IsoDateTimeType()
    owner_token = StringType()
    owner = StringType()
    procurementMethodType = StringType()
    revisions = ListType(ModelType(Revision), default=list())

    __name__ = ''

    def __acl__(self):
        acl = [
            # (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            # for i in self.bids
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_plan'),
        ])
        return acl

    def __repr__(self):
        return '<%s:%r@%r>' % (type(self).__name__, self.id, self.rev)

    @serializable(serialized_name='id')
    def doc_id(self):
        """A property that is serialized by schematics exports."""
        return self._id

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param kw:
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if not data[k]]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self
