# -*- coding: utf-8 -*-
from schematics.types import StringType, FloatType
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from zope.interface import implementer
from pyramid.security import Allow
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    Model, Identifier, plain_role,
    listing_role, schematics_default_role,
    schematics_embedded_role, ListType, SifterListType,
    BooleanType, Value as BaseValue, CPVClassification as BaseCPVClassification
)
from openprocurement.api.utils import (
    get_now
)
from openprocurement.api.validation import (
    validate_cpv_group, validate_items_uniq
)
from openprocurement.tender.core.models import (
    ITender, validate_features_uniq,
    validate_values_uniq, Feature as BaseFeature,
    FeatureValue as BaseFeatureValue, create_role,
    edit_role, view_role, enquiries_role,
    chronograph_role, chronograph_view_role,
    Administrator_role, ProcuringEntity as BaseProcuringEntity,
    get_tender, PeriodStartEndRequired,
    validate_lots_uniq, Lot as BaseLotUA
)
from openprocurement.tender.core.utils import (
    calculate_business_date
)
from openprocurement.tender.openua.models import (
    Item as BaseUAItem,
    Tender as BaseTenderUA,
)
from openprocurement.tender.openua.constants import (
    TENDER_PERIOD as TENDERING_DURATION_UA,
)
from openprocurement.tender.openeu.models import (
    Administrator_bid_role, view_bid_role,
    pre_qualifications_role, ConfidentialDocument,
    auction_patch_role, auction_view_role,
    auction_post_role, embedded_lot_role,
    default_lot_role, Lot as BaseLotEU,
    Item as BaseEUItem, LotValue as BaseLotValueEU,
    Tender as BaseTenderEU, Bid as BidEU
)
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION as TENDERING_DURATION_EU,
)
from openprocurement.tender.competitivedialogue.utils import (
    validate_features_custom_weight
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_UA_TYPE, CD_EU_TYPE,
    STAGE_2_EU_TYPE, STAGE_2_UA_TYPE,
    STAGE2_STATUS, FEATURES_MAX_SUM
)


edit_role_ua = edit_role + blacklist('enquiryPeriod', 'status')
edit_stage2_pending = whitelist('status')
edit_stage2_waiting = whitelist('status', 'stage2TenderID')
view_role_stage1 = (view_role + blacklist('auctionPeriod'))
pre_qualifications_role_stage1 = (pre_qualifications_role
                                  + blacklist('auctionPeriod'))

roles = {
    'plain': plain_role,
    'create': create_role,
    'view': view_role_stage1,
    'listing': listing_role,
    'active.pre-qualification': pre_qualifications_role_stage1,
    'active.pre-qualification.stand-still': pre_qualifications_role_stage1,
    'active.stage2.pending': pre_qualifications_role_stage1,
    'active.stage2.waiting': pre_qualifications_role_stage1,
    'edit_active.stage2.pending': whitelist('status'),
    'draft': (enquiries_role + blacklist('auctionPeriod')),
    'active.tendering': (enquiries_role + blacklist('auctionPeriod')),
    'complete': view_role_stage1,
    'unsuccessful': view_role_stage1,

    'cancelled': view_role_stage1,
    'chronograph': chronograph_role,
    'chronograph_view': chronograph_view_role,
    'Administrator': Administrator_role,
    'default': schematics_default_role,
    'contracting': whitelist('doc_id', 'owner'),
    'competitive_dialogue': edit_stage2_waiting
}


class ICDEUTender(ITender):
    """ Marker interface for Competitive Dialogue EU tenders """


class ICDUATender(ITender):
    """ Marker interface for Competitive Dialogue UA tenders """


class ICDEUStage2Tender(ITender):
    """ Marker interface for Competitive Dialogue EU Stage 2 tenders """


class ICDUAStage2Tender(ITender):
    """ Marker interface for Competitive Dialogue UA Stage 2 tenders """


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


class LotValue(BaseLotValueEU):

    class Options:
        roles = {
            'create': whitelist('relatedLot', 'subcontractingDetails'),
            'edit': whitelist('relatedLot', 'subcontractingDetails'),
            'view': (schematics_default_role + blacklist('value')),
        }

    value = ModelType(BaseValue, required=False)

    def validate_value(self, *args, **kwargs):
        pass  # remove validation

view_bid_role_stage1 = (view_bid_role + blacklist('value'))

class Bid(BidEU):
    class Options:
        roles = {
            'Administrator': Administrator_bid_role,
            'embedded': view_bid_role_stage1,
            'view': view_bid_role_stage1,
            'create': whitelist('tenderers', 'lotValues',
                                'status', 'selfQualified', 'selfEligible', 'subcontractingDetails',
                                'documents'),
            'edit': whitelist('tenderers', 'lotValues', 'status', 'subcontractingDetails'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.pre-qualification': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.pre-qualification.stand-still': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.auction': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.stage2.pending': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.stage2.waiting': whitelist('id', 'status', 'documents', 'tenderers'),
            'active.qualification': view_bid_role,
            'complete': view_bid_role_stage1,
            'unsuccessful': view_bid_role_stage1,
            'cancelled': view_bid_role_stage1,
            'invalid': whitelist('id', 'status'),
            'deleted': whitelist('id', 'status'),
        }

    documents = ListType(ModelType(Document), default=list())
    value = None
    lotValues = ListType(ModelType(LotValue), default=list())

    def validate_value(self, *args, **kwargs):
        pass  # remove validation on stage 1

    def validate_parameters(self, data, parameters):
        pass  # remove validation on stage 1


class FeatureValue(BaseFeatureValue):
    value = FloatType(required=True, min_value=0.0, max_value=FEATURES_MAX_SUM)


class Feature(BaseFeature):
    enum = ListType(ModelType(FeatureValue), default=list(), min_size=1, validators=[validate_values_uniq])

lot_roles = {
    'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
    'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
    'embedded': embedded_lot_role,
    'view': default_lot_role,
    'default': default_lot_role,
    'chronograph': whitelist('id', 'auctionPeriod'),
    'chronograph_view': whitelist('id', 'auctionPeriod', 'numberOfBids', 'status'),
}


class Lot(BaseLotEU):

    class Options:
        roles = {
            'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
            'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
            'embedded': embedded_lot_role,
            'view': (default_lot_role + blacklist('auctionPeriod')),
            'default': (default_lot_role + blacklist('auctionPeriod')),
            'chronograph': whitelist('id'),
            'chronograph_view': whitelist('id', 'numberOfBids', 'status'),
        }

LotStage1 = Lot


@implementer(ICDEUTender)
class Tender(BaseTenderEU):
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
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])

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

    def validate_features(self, data, features):
        validate_features_custom_weight(self, data, features, FEATURES_MAX_SUM)


CompetitiveDialogEU = Tender


class LotId(Model):
    id = StringType()

    def validate_id(self, data, lot_id):
        if lot_id and isinstance(data['__parent__'], Model) and lot_id not in [i.id for i in get_tender(data['__parent__']).lots]:
            raise ValidationError(u"id should be one of lots")


class Firms(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(LotId), default=list())


@implementer(ICDUATender)
class Tender(CompetitiveDialogEU):
    procurementMethodType = StringType(default=CD_UA_TYPE)
    title_en = StringType()
    items = ListType(ModelType(BaseUAItem), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])
    procuringEntity = ModelType(BaseProcuringEntity, required=True)
    stage2TenderID = StringType(required=False)


CompetitiveDialogUA = Tender


# stage 2 models

hide_dialogue_token = blacklist('dialogue_token')
close_edit_technical_fields = blacklist('dialogue_token', 'shortlistedFirms', 'dialogueID', 'value', 'features')


stage_2_roles = {
    'plain': plain_role,
    'create': (blacklist('owner_token', 'tenderPeriod', '_attachments', 'revisions', 'dateModified', 'doc_id', 'bids', 'documents', 'awards', 'questions', 'complaints', 'auctionUrl', 'status', 'auctionPeriod', 'awardPeriod', 'awardCriteria', 'submissionMethod', 'cancellations', 'procurementMethod') + schematics_embedded_role),
    'edit': whitelist('tenderPeriod'),
    'edit_draft': whitelist('status'),  # only bridge must change only status
    'edit_'+STAGE2_STATUS: whitelist('tenderPeriod', 'status'),
    'edit_active.tendering': whitelist('tenderPeriod', 'items'),
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
    'draft': enquiries_role + blacklist('dialogue_token', 'shortlistedFirms'),
    'draft.stage2': enquiries_role + hide_dialogue_token,
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
    'competitive_dialogue': edit_stage2_waiting
}


def init_PeriodStartEndRequired(tendering_duration):
    def wrapper():
        return PeriodStartEndRequired({"startDate": get_now(),
                                       "endDate": calculate_business_date(get_now(), tendering_duration)})
    return wrapper


def stage2__acl__(obj):
    acl = [
        (Allow, '{}_{}'.format(obj.owner, obj.dialogue_token), 'generate_credentials')
    ]
    acl.extend([
               (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_qualification_complaint')
               for i in obj.bids
               if i.status in ['active', 'unsuccessful']
               ])
    acl.extend([
               (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
               for i in obj.bids
               if i.status == 'active'])
    acl.extend([
        (Allow, '{}_{}'.format(obj.owner, obj.owner_token), 'edit_tender'),
        (Allow, '{}_{}'.format(obj.owner, obj.owner_token), 'upload_tender_documents'),
        (Allow, '{}_{}'.format(obj.owner, obj.owner_token), 'edit_complaint'),
        (Allow, 'g:competitive_dialogue', 'edit_tender')
    ])
    return acl


lot_stage2_roles = {
    'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
    'edit': whitelist(),
    'embedded': embedded_lot_role,
    'view': default_lot_role,
    'default': default_lot_role,
    'auction_view': default_lot_role,
    'auction_patch': whitelist('id', 'auctionUrl'),
    'chronograph': whitelist('id', 'auctionPeriod'),
    'chronograph_view': whitelist('id', 'auctionPeriod', 'numberOfBids', 'status'),
}


class Lot(BaseLotUA):

    class Options:
        roles = lot_stage2_roles

LotStage2UA = Lot


class Lot(BaseLotEU):

    class Options:
        roles = lot_stage2_roles

LotStage2EU = Lot


class CPVClassification(BaseCPVClassification):

    def validate_scheme(self, data, scheme):
        pass


class Item(BaseEUItem):

    class Options:
        roles = {'edit_active.tendering': whitelist('deliveryDate')}

    classification = ModelType(CPVClassification, required=True)

ItemStage2EU = Item


class Item(BaseUAItem):

    class Options:
        roles = {'edit_active.tendering': whitelist('deliveryDate')}

    classification = ModelType(CPVClassification, required=True)


ItemStage2UA = Item


class Award(BaseTenderEU.awards.model_class):

    items = ListType(ModelType(ItemStage2EU))


class Contract(BaseTenderEU.contracts.model_class):

    items = ListType(ModelType(ItemStage2EU))


@implementer(ICDEUStage2Tender)
class Tender(BaseTenderEU):
    procurementMethodType = StringType(default=STAGE_2_EU_TYPE)
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms), min_size=3, required=True)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=False,
                             default=init_PeriodStartEndRequired(TENDERING_DURATION_EU))
    status = StringType(
        choices=['draft', 'active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still',
                 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled',
                 'unsuccessful', STAGE2_STATUS],
        default='active.tendering')
    lots = ListType(ModelType(LotStage2EU), default=list(), validators=[validate_lots_uniq])
    procurementMethod = StringType(choices=['open', 'selective', 'limited'], default='selective')

    # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    items = ListType(ModelType(ItemStage2EU), required=True, min_size=1, validators=[validate_cpv_group,
                                                                                     validate_items_uniq])
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])

    create_accreditation = 'c'

    class Options:
        roles = stage_2_roles.copy()

    def __acl__(self):
        return stage2__acl__(self)

    def validate_features(self, data, features):
        validate_features_custom_weight(self, data, features, FEATURES_MAX_SUM)

TenderStage2EU = Tender


class Award(BaseTenderUA.awards.model_class):

    items = ListType(ModelType(ItemStage2UA))


class Contract(BaseTenderUA.contracts.model_class):

    items = ListType(ModelType(ItemStage2UA))


@implementer(ICDUAStage2Tender)
class Tender(BaseTenderUA):
    procurementMethodType = StringType(default=STAGE_2_UA_TYPE)
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(Firms), min_size=3, required=True)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=False,
                             default=init_PeriodStartEndRequired(TENDERING_DURATION_UA))
    status = StringType(
        choices=['draft', 'active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still',
                 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled',
                 'unsuccessful', STAGE2_STATUS],
        default='active.tendering')
    lots = ListType(ModelType(LotStage2UA), default=list(), validators=[validate_lots_uniq])
    items = ListType(ModelType(ItemStage2UA), required=True, min_size=1, validators=[validate_cpv_group,
                                                                                     validate_items_uniq])
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    procurementMethod = StringType(choices=['open', 'selective', 'limited'], default='selective')

    create_accreditation = 'c'

    class Options:
        roles = stage_2_roles.copy()

    def __acl__(self):
        return stage2__acl__(self)

    def validate_features(self, data, features):
        validate_features_custom_weight(self, data, features, FEATURES_MAX_SUM)

TenderStage2UA = Tender
