# -*- coding: utf-8 -*-
import os
from uuid import uuid4
from couchdb_schematics.document import SchematicsDocument
from schematics.exceptions import ValidationError
from openprocurement.api.models import Model, Period, Revision
from openprocurement.api.models import Document as BaseDocument
from openprocurement.api.models import Unit, CPVClassification, Classification, Identifier
from openprocurement.api.models import schematics_embedded_role, schematics_default_role, IsoDateTimeType, ListType, MD5Type
from openprocurement.api.models import validate_cpv_group, validate_items_uniq, validate_dkpp, get_now
from pyramid.security import Allow
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, IntType, FloatType, BaseType
from schematics.types.compound import ModelType, DictType
from schematics.types.serializable import serializable
from zope.interface import implementer, Interface
from itertools import chain


class IPlan(Interface):
    """ Base plan marker interface """


class Project(Model):
    """A project """
    id = StringType(required=True)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()


class Budget(Model):
    """A budget model """
    id = StringType(required=True)
    description = StringType(required=True)
    description_en = StringType()
    description_ru = StringType()
    amount = FloatType(required=True)
    currency = StringType(required=False, default=u'UAH', max_length=3,
                          min_length=3)  # The currency in 3-letter ISO 4217 format.
    amountNet = FloatType()
    project = ModelType(Project)
    year = IntType(min_value=2000)
    notes = StringType()


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
    description_en = StringType()
    description_ru = StringType()

    def validate_classification(self, data, classification):
        base_cpv_code = data['__parent__'].classification.id[:3]
        if (base_cpv_code != classification.id[:3]):
            raise ValidationError(u"CPV group of items be identical to root cpv")


class PlanOrganization(Model):
    """An organization"""
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)

PROCEDURES = {
  '': ('',),
  'open': ('belowThreshold', 'aboveThresholdUA', 'aboveThresholdEU', 'aboveThresholdUA.defense'),
  'limited': ('reporting', 'negotiation', 'negotiation.quick'),
}

class PlanTender(Model):
    """Tender for planning model """
    procurementMethod = StringType(choices=PROCEDURES.keys(), default='')
    procurementMethodType = StringType(choices=list(chain(*PROCEDURES.values())), default='')
    tenderPeriod = ModelType(Period, required=True)

    def validate_procurementMethodType(self, data, procurementMethodType):
        if (procurementMethodType not in PROCEDURES[data.get('procurementMethod')]):
            raise ValidationError(u"Value must be one of {!r}.".format(PROCEDURES[data.get('procurementMethod')]))


class Document(BaseDocument):
    documentOf = StringType(required=False)


# roles
plain_role = (blacklist('_attachments', 'revisions', 'dateModified') + schematics_embedded_role)
create_role = (blacklist('owner_token', 'owner', '_attachments', 'revisions', 'dateModified', 'datePublished', 'planID', 'doc_id', '_attachments') + schematics_embedded_role)
edit_role = (
    blacklist('owner_token', 'owner', '_attachments', 'revisions', 'dateModified', 'datePublished', 'doc_id', 'planID', 'mode', '_attachments') + schematics_embedded_role)
view_role = (blacklist('owner_token', '_attachments', 'revisions') + schematics_embedded_role)
listing_role = whitelist('dateModified', 'doc_id')
revision_role = whitelist('revisions')
Administrator_role = whitelist('status', 'mode', 'procuringEntity')


@implementer(IPlan)
class Plan(SchematicsDocument, Model):
    """Plan model"""

    class Options:
        roles = {
            'plain': plain_role,
            'revision': revision_role,
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

    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the tender.

    planID = StringType()
    mode = StringType(choices=['test'])  # flag for test data ?
    items = ListType(ModelType(PlanItem), required=False, validators=[validate_cpv_group, validate_items_uniq])

    _attachments = DictType(DictType(BaseType), default=dict())  # couchdb attachments
    dateModified = IsoDateTimeType()
    datePublished = IsoDateTimeType(default=get_now)
    owner_token = StringType()
    owner = StringType()
    procurementMethodType = StringType()
    revisions = ListType(ModelType(Revision), default=list())

    create_accreditation = 3

    __name__ = ''

    def __acl__(self):
        acl = [
            # (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            # for i in self.bids
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_plan'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_plan_documents'),
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
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)]
        for k in del_keys:
            del data[k]

        self._data.update(data)
        return self
