# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.exceptions import ValidationError
from zope.interface import implementer
from schematics.types.compound import ModelType
from openprocurement.api.models import ITender
from openprocurement.tender.openua.models import SifterListType, Item as BaseItem
from openprocurement.tender.openeu.models import (Tender as TenderEU, Administrator_bid_role, view_bid_role,
                                                  Organization as BaseOrganization, Bid as BidEU, ConfidentialDocument)
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, listing_role,
    enquiries_role, validate_cpv_group, validate_items_uniq,
    chronograph_role, chronograph_view_role,
    Identifier as BaseIdentifier, ContactPoint as BaseContactPoint,
    Administrator_role, schematics_default_role,
    schematics_embedded_role, ListType, BooleanType
)
from schematics.transforms import whitelist, blacklist
from openprocurement.tender.openeu.models import pre_qualifications_role

edit_role_ua = edit_role + blacklist('enquiryPeriod', 'status')

roles = {
    'plain': plain_role,
    'create': create_role,
    'view': view_role,
    'listing': listing_role,
    'active.pre-qualification': pre_qualifications_role,
    'active.pre-qualification.stand-still': pre_qualifications_role,
    'active.stage2.pending': enquiries_role,
    'active.stage2.waiting': pre_qualifications_role,
    'edit_active.stage2.pending': pre_qualifications_role,
    'draft': enquiries_role,
    'active.tendering': enquiries_role,
    'complete': view_role,
    'unsuccessful': view_role,
    'cancelled': view_role,
    'chronograph': chronograph_role,
    'chronograph_view': chronograph_view_role,
    'Administrator': Administrator_role,
    'default': schematics_default_role,
    'contracting': whitelist('doc_id', 'owner'),
}


class Organization(BaseOrganization):
    """Redefinition model Organization for UA dialogue"""

    name_en = StringType()  # not required for UA dialogue
    identifier = ModelType(BaseIdentifier, required=True)
    contactPoint = ModelType(BaseContactPoint, required=True)


class ProcuringEntity(Organization):
    """Redefinition model ProcuringEntity for UA dialogue"""

    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'edit_active.tendering': schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=['general', 'special', 'defense', 'other'])


class Document(ConfidentialDocument):
    """ Document model with new feature as Description of the decision to purchase """

    class Options:
        roles = {
            'edit': blacklist('id', 'url', 'datePublished', 'dateModified', ''),
            'embedded': schematics_embedded_role,
            'view': (blacklist('revisions') + schematics_default_role),
            'restricted_view': (blacklist('revisions', 'url') + schematics_default_role),
            'revisions': whitelist('url', 'dateModified'),
        }

    isDescriptionDecision = BooleanType(default=False)

    def validate_confidentialityRationale(self, data, val):
        if data['confidentiality'] != 'public' and not data['isDescriptionDecision']:
            if not val:
                raise ValidationError(u"confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError(u"confidentialityRationale should contain at least 30 characters")


class Bid(BidEU):
    class Options:
        roles = {
            'Administrator': Administrator_bid_role,
            'embedded': view_bid_role,
            'view': view_bid_role,
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues',
                                'status', 'selfQualified', 'selfEligible', 'subcontractingDetails'),
            'edit': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'subcontractingDetails'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.pre-qualification': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.pre-qualification.stand-still': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.auction': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.stage2.pending': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.qualification': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful': view_bid_role,
            'bid.unsuccessful': whitelist('id', 'status', 'tenderers', 'parameters',
                                          'selfQualified', 'selfEligible', 'subcontractingDetails'),
            'cancelled': view_bid_role,
            'invalid': whitelist('id', 'status'),
            'deleted': whitelist('id', 'status'),
        }

    documents = ListType(ModelType(Document), default=list())


@implementer(ITender)
class Tender(TenderEU):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdEU")
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification',
                                 'active.pre-qualification.stand-still', 'active.stage2.pending',
                                 'active.stage2.waiting', 'complete', 'cancelled', 'unsuccessful'],
                        default='active.tendering')
    # A list of all the companies who entered submissions for the tender.
    bids = SifterListType(ModelType(Bid), default=list(),
                          filter_by='status', filter_in_values=['invalid', 'deleted'])
    TenderID = StringType(required=False)

    class Options:
        roles = roles.copy()


CompetitiveDialogEU = Tender


@implementer(ITender)
class Tender(CompetitiveDialogEU):
    procurementMethodType = StringType(default="competitiveDialogue.aboveThresholdUA")
    title_en = StringType()
    items = ListType(ModelType(BaseItem), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])
    procuringEntity = ModelType(ProcuringEntity, required=True)


CompetitiveDialogUA = Tender
