# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.exceptions import ValidationError
from zope.interface import implementer
from pyramid.security import Allow
from schematics.types.compound import ModelType
from openprocurement.api.models import ITender, Identifier, Model
from openprocurement.tender.openua.models import SifterListType, Item as BaseItem
from openprocurement.tender.openeu.models import (Tender as TenderEU, Administrator_bid_role, view_bid_role,
                                                  pre_qualifications_role, Bid as BidEU, ConfidentialDocument,
                                                  edit_role_eu, auction_patch_role, auction_view_role,
                                                  auction_post_role)
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, listing_role,
    enquiries_role, validate_cpv_group, validate_items_uniq,
    chronograph_role, chronograph_view_role, ProcuringEntity as BaseProcuringEntity,
    Administrator_role, schematics_default_role,
    schematics_embedded_role, ListType, BooleanType
)
from schematics.transforms import whitelist, blacklist

# constants for procurementMethodtype
CD_UA_TYPE = "competitiveDialogueUA"
CD_EU_TYPE = "competitiveDialogueEU"
STAGE_2_EU_TYPE = "competitiveDialogueEU.stage2"
STAGE_2_UA_TYPE = "competitiveDialogueUA.stage2"

edit_role_ua = edit_role + blacklist('enquiryPeriod', 'status')
edit_stage2_pending = whitelist('status')
edit_stage2_waiting = whitelist('status', 'stage2TenderID')

roles = {
    'plain': plain_role,
    'create': create_role,
    'view': view_role,
    'listing': listing_role,
    'active.pre-qualification': pre_qualifications_role,
    'active.pre-qualification.stand-still': pre_qualifications_role,
    'active.stage2.pending': enquiries_role,
    'active.stage2.waiting': pre_qualifications_role,
    'edit_active.stage2.pending': whitelist('status'),
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
    'competitive_dialogue': edit_stage2_waiting,
}


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
    procurementMethodType = StringType(default=CD_EU_TYPE)
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification',
                                 'active.pre-qualification.stand-still', 'active.stage2.pending',
                                 'active.stage2.waiting', 'complete', 'cancelled', 'unsuccessful'],
                        default='active.tendering')
    # A list of all the companies who entered submissions for the tender.
    bids = SifterListType(ModelType(Bid), default=list(),
                          filter_by='status', filter_in_values=['invalid', 'deleted'])
    TenderID = StringType(required=False)
    stage2TenderID = StringType(required=False)

    class Options:
        roles = roles.copy()

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'competitive_dialogue':
            role = 'competitive_dialogue'
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_qualification_complaint')
            for i in self.bids
            if i.status in ['active', 'unsuccessful']
            ]
        acl.extend(
            [(Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
             for i in self.bids
             if i.status == 'active'
             ])
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
            (Allow, 'g:competitive_dialogue', 'extract_credentials'),
            (Allow, 'g:competitive_dialogue', 'edit_tender'),
        ])
        return acl


CompetitiveDialogEU = Tender


class LotId(Model):
    id = StringType()


class Firms(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(LotId), default=list())


@implementer(ITender)
class Tender(CompetitiveDialogEU):
    procurementMethodType = StringType(default=CD_UA_TYPE)
    title_en = StringType()
    items = ListType(ModelType(BaseItem), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])
    procuringEntity = ModelType(BaseProcuringEntity, required=True)
    stage2TenderID = StringType(required=False)


CompetitiveDialogUA = Tender


# stage 2 models

hide_dialogue_token = blacklist('dialogue_token')
close_edit_technical_fields = blacklist('dialogue_token', 'shortlistedFirms', 'dialogueID')


stage_2_roles = {
    'plain': plain_role,
    'create': (blacklist('owner_token', '_attachments', 'revisions', 'dateModified', 'doc_id', 'tenderID', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'status', 'auctionPeriod', 'awardPeriod', 'awardCriteria', 'submissionMethod', 'cancellations') + schematics_embedded_role),
    'edit': edit_role_eu + close_edit_technical_fields,
    'edit_draft': edit_role_eu + close_edit_technical_fields,
    'edit_active.tendering': edit_role_eu + close_edit_technical_fields,
    'edit_active.pre-qualification': whitelist('status'),
    'edit_active.pre-qualification.stand-still': whitelist(),
    'edit_active.auction': whitelist(),
    'edit_active.qualification': whitelist(),
    'edit_active.awarded': whitelist(),
    'edit_complete': whitelist(),
    'edit_unsuccessful': whitelist(),
    'edit_cancelled': whitelist(),
    'view': view_role + hide_dialogue_token,
    'listing': listing_role,
    'auction_view': auction_view_role,
    'auction_post': auction_post_role,
    'auction_patch': auction_patch_role,
    'draft': enquiries_role + hide_dialogue_token,
    'active.tendering': enquiries_role + hide_dialogue_token,
    'active.pre-qualification': pre_qualifications_role + hide_dialogue_token,
    'active.pre-qualification.stand-still': pre_qualifications_role + hide_dialogue_token,
    'active.auction': pre_qualifications_role + hide_dialogue_token,
    'active.qualification': view_role + hide_dialogue_token,
    'active.awarded': view_role + hide_dialogue_token,
    'complete': view_role + hide_dialogue_token,
    'unsuccessful': view_role + hide_dialogue_token,
    'cancelled': view_role + hide_dialogue_token,
    'chronograph': chronograph_role,
    'chronograph_view': chronograph_view_role,
    'Administrator': Administrator_role,
    'default': schematics_default_role,
    'contracting': whitelist('doc_id', 'owner'),
}


@implementer(ITender)
class Tender(TenderEU):
    procurementMethodType = StringType(default=STAGE_2_EU_TYPE)
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms), required=True)

    class Options:
        roles = stage_2_roles.copy()

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(self.owner, self.dialogue_token), 'generate_credentials')
        ]
        acl.extend([
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_qualification_complaint')
            for i in self.bids
            if i.status in ['active', 'unsuccessful']
            ])
        acl.extend([
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
            if i.status == 'active'
            ])
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint')
        ])
        return acl


TenderStage2EU = Tender


@implementer(ITender)
class Tender(TenderStage2EU):
    procurementMethodType = StringType(default=STAGE_2_UA_TYPE)
    title_en = StringType()

TenderStage2UA = Tender
