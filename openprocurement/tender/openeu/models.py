from uuid import uuid4
from datetime import timedelta
from iso8601 import parse_date
from pyramid.security import Allow
from zope.interface import implementer
from schematics.types import StringType, MD5Type, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.transforms import blacklist, whitelist
from schematics.exceptions import ValidationError
from openprocurement.api.models import (
    ITender, TZ, Model, Address, Period, IsoDateTimeType, ListType,
    Tender as BaseTender, Identifier as BaseIdentifier, Bid as BaseBid,
    Contract as BaseContract, Cancellation as BaseCancellation, Lot as BaseLot,
    Document as BaseDocument, ContactPoint as BaseContactPoint,
    LotValue as BaseLotValue, ComplaintModelType as BaseComplaintModelType,
    plain_role, create_role, edit_role, view_role, listing_role, draft_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, view_bid_role,
    Administrator_bid_role, Administrator_role, schematics_default_role,
    schematics_embedded_role, get_now, embedded_lot_role, default_lot_role,
    calc_auction_end_time, get_tender, validate_lots_uniq,
    validate_cpv_group, validate_items_uniq, rounding_shouldStartAfter,
)
from openprocurement.tender.openua.utils import (
    calculate_business_date,
)
from openprocurement.tender.openua.models import (
    Complaint as BaseComplaint, Award as BaseAward, Item as BaseItem,
    PeriodStartEndRequired, SifterListType, COMPLAINT_SUBMIT_TIME,
    EnquiryPeriod, ENQUIRY_STAND_STILL_TIME, AUCTION_PERIOD_TIME,
    calculate_normalized_date, Tender as OpenUATender,
)

eu_role = blacklist('enquiryPeriod', 'qualifications')
edit_role_eu = edit_role + eu_role
create_role_eu = create_role + eu_role
pre_qualifications_role = (blacklist('owner_token', '_attachments', 'revisions') + schematics_embedded_role)
eu_auction_role = auction_role

TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
TENDERING_AUCTION = timedelta(days=35)
QUESTIONS_STAND_STILL = timedelta(days=10)
PREQUALIFICATION_COMPLAINT_STAND_STILL = timedelta(days=5)
COMPLAINT_STAND_STILL = timedelta(days=10)


def bids_validation_wrapper(validation_func):
    def validator(klass, data, value):
        if data['status'] in ('deleted', 'invalid', 'draft'):
            # skip not valid bids
            return
        tender = data['__parent__']
        request = tender.__parent__.request
        if request.method == "PATCH" and isinstance(tender, Tender) and request.authenticated_role == "tender_owner":
            # disable bids validation on tender PATCH requests as tender bids will be invalidated
            return
        return validation_func(klass, data, value)
    return validator


class ComplaintModelType(BaseComplaintModelType):
    view_claim_statuses = ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    description_en = StringType(required=True, min_length=1)


class Identifier(BaseIdentifier):

    legalName_en = StringType(required=True, min_length=1)


class ContactPoint(BaseContactPoint):

    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, choices=['uk', 'en', 'ru'], default='uk')


class Organization(Model):
    """An organization."""
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    name = StringType(required=True)
    name_en = StringType(required=True, min_length=1)
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True),
                                       required=False)


class ProcuringEntity(Organization):
    """An organization."""
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'edit_active.tendering': schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=['general', 'special', 'defense', 'other'])


class Document(BaseDocument):

    language = StringType(required=True, choices=['uk', 'en', 'ru'], default='uk')


class ConfidentialDocument(Document):
    """ Confidential Document """
    class Options:
        roles = {
            'edit': blacklist('id', 'url', 'datePublished', 'dateModified', 'author', 'md5', 'download_url'),
            'embedded': schematics_embedded_role,
            'view': (blacklist('revisions') + schematics_default_role),
            'restricted_view': (blacklist('revisions', 'url', 'download_url') + schematics_default_role),
            'revisions': whitelist('url', 'dateModified'),
        }

    confidentiality = StringType(choices=['public', 'buyerOnly'], default='public')
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        if data['confidentiality'] != 'public':
            if not val:
                raise ValidationError(u"confidentialityRationale is required")
            elif len(val) < 30:
                raise ValidationError(u"confidentialityRationale should contain at least 30 characters")


class Contract(BaseContract):
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))


class Complaint(BaseComplaint):
    class Options:
        roles = {
            'active.pre-qualification': view_bid_role,
            'active.pre-qualification.stand-still': view_bid_role,
        }
    documents = ListType(ModelType(Document), default=list())

    def serialize(self, role=None, context=None):
        if role == 'view' and self.type == 'claim' and get_tender(self).status in ['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction']:
            role = 'view_claim'
        return super(Complaint, self).serialize(role=role, context=context)


class Cancellation(BaseCancellation):
    class Options:
        roles = {
            'create': whitelist('reason', 'status', 'reasonType', 'cancellationOf', 'relatedLot'),
            'edit': whitelist('status', 'reasonType'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    documents = ListType(ModelType(Document), default=list())
    reasonType = StringType(choices=['cancelled', 'unsuccessful'], default='cancelled')


class TenderAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = self.__parent__
        if tender.lots or tender.status not in ['active.tendering', 'active.pre-qualification.stand-still', 'active.auction']:
            return
        start_after = None
        if tender.status == 'active.tendering' and tender.tenderPeriod.endDate:
            start_after = calculate_business_date(tender.tenderPeriod.endDate, TENDERING_AUCTION, tender)
        elif self.startDate and get_now() > calc_auction_end_time(tender.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(tender.numberOfBids, self.startDate)
        elif tender.qualificationPeriod and tender.qualificationPeriod.endDate:
            start_after = tender.qualificationPeriod.endDate
        if start_after:
            return rounding_shouldStartAfter(start_after, tender).isoformat()


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        if tender.status not in ['active.tendering', 'active.pre-qualification.stand-still', 'active.auction'] or lot.status != 'active':
            return
        start_after = None
        if tender.status == 'active.tendering' and tender.tenderPeriod.endDate:
            start_after = calculate_business_date(tender.tenderPeriod.endDate, TENDERING_AUCTION, tender)
        elif self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(lot.numberOfBids, self.startDate)
        elif tender.qualificationPeriod and tender.qualificationPeriod.endDate:
            start_after = tender.qualificationPeriod.endDate
        if start_after:
            return rounding_shouldStartAfter(start_after, tender).isoformat()


class Lot(BaseLot):

    class Options:
        roles = {
            'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
            'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'guarantee', 'minimalStep'),
            'embedded': embedded_lot_role,
            'view': default_lot_role,
            'default': default_lot_role,
            'auction_view': default_lot_role,
            'auction_patch': whitelist('id', 'auctionUrl'),
            'chronograph': whitelist('id', 'auctionPeriod'),
            'chronograph_view': whitelist('id', 'auctionPeriod', 'numberOfBids', 'status'),
        }

    auctionPeriod = ModelType(LotAuctionPeriod, default={})

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues if i.status in ["active", "pending"]] and bid.status in ["active", "pending"]
        ]
        return len(bids)


class LotValue(BaseLotValue):
    class Options:
        roles = {
            'create': whitelist('value', 'relatedLot', 'subcontractingDetails'),
            'edit': whitelist('value', 'relatedLot', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'date', 'relatedLot', 'participationUrl', 'status',),
        }

    subcontractingDetails = StringType()
    status = StringType(choices=['pending', 'active', 'unsuccessful'],
                        default='pending')

    def validate_value(self, data, value):
        if value and isinstance(data['__parent__'], Model) and (data['__parent__'].status not in ('invalid', 'deleted')) and data['relatedLot']:
            lots = [i for i in get_tender(data['__parent__']).lots if i.id == data['relatedLot']]
            if not lots:
                return
            lot = lots[0]
            if lot.value.amount < value.amount:
                raise ValidationError(u"value of bid should be less than value of lot")
            if lot.get('value').currency != value.currency:
                raise ValidationError(u"currency of bid should be identical to currency of value of lot")
            if lot.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of value of lot")

    def validate_relatedLot(self, data, relatedLot):
        if isinstance(data['__parent__'], Model) and (data['__parent__'].status not in ('invalid', 'deleted')) and relatedLot not in [i.id for i in get_tender(data['__parent__']).lots]:
            raise ValidationError(u"relatedLot should be one of lots")


class Bid(BaseBid):
    class Options:
        roles = {
            'Administrator': Administrator_bid_role,
            'embedded': view_bid_role,
            'view': view_bid_role,
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'selfQualified', 'selfEligible', 'subcontractingDetails'),
            'edit': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'status'),
            'auction_post': whitelist('value', 'lotValues', 'id', 'date'),
            'auction_patch': whitelist('id', 'lotValues', 'participationUrl'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.pre-qualification': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'active.pre-qualification.stand-still': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'active.auction': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'active.qualification': view_bid_role,
            'active.awarded': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful': view_bid_role,
            'bid.unsuccessful':  whitelist('id', 'status', 'tenderers', 'documents', 'eligibilityDocuments', 'parameters', 'selfQualified', 'selfEligible', 'subcontractingDetails'),
            'cancelled': view_bid_role,
            'invalid': whitelist('id', 'status'),
            'invalid.pre-qualification': whitelist('id', 'status', 'documents', 'eligibilityDocuments', 'tenderers'),
            'deleted': whitelist('id', 'status'),
        }
    documents = ListType(ModelType(ConfidentialDocument), default=list())
    financialDocuments = ListType(ModelType(ConfidentialDocument), default=list())
    eligibilityDocuments = ListType(ModelType(ConfidentialDocument), default=list())
    qualificationDocuments = ListType(ModelType(ConfidentialDocument), default=list())
    lotValues = ListType(ModelType(LotValue), default=list())
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(required=True, choices=[True])
    subcontractingDetails = StringType()
    status = StringType(choices=['draft','pending', 'active', 'invalid', 'invalid.pre-qualification', 'unsuccessful', 'deleted'],
                        default='pending')

    def serialize(self, role=None):
        if role and role != 'create' and self.status in ['invalid', 'invalid.pre-qualification', 'deleted']:
            role = self.status
        elif role and role != 'create' and self.status == 'unsuccessful':
            role = 'bid.unsuccessful'
        return super(Bid, self).serialize(role)

    @serializable(serialized_name="status")
    def serialize_status(self):
        if self.status in ['draft', 'invalid', 'deleted'] or self.__parent__.status in ['active.tendering', 'cancelled']:
            return self.status
        if self.__parent__.lots:
            active_lots = [lot.id for lot in self.__parent__.lots if lot.status in ('active', 'complete',)]
            if not self.lotValues:
                return 'invalid'
            elif [i.relatedLot for i in self.lotValues if i.status == 'pending' and i.relatedLot in active_lots]:
                return 'pending'
            elif [i.relatedLot for i in self.lotValues if i.status == 'active' and i.relatedLot in active_lots]:
                return 'active'
            else:
                return 'unsuccessful'
        return self.status

    @bids_validation_wrapper
    def validate_value(self, data, value):
        BaseBid._validator_functions['value'](self, data, value)

    @bids_validation_wrapper
    def validate_lotValues(self, data, lotValues):
        BaseBid._validator_functions['lotValues'](self, data, lotValues)

    @bids_validation_wrapper
    def validate_participationUrl(self, data, participationUrl):
        BaseBid._validator_functions['participationUrl'](self, data, participationUrl)

    @bids_validation_wrapper
    def validate_parameters(self, data, parameters):
        BaseBid._validator_functions['parameters'](self, data, parameters)


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    complaints = ListType(ModelType(Complaint), default=list())
    items = ListType(ModelType(Item))
    documents = ListType(ModelType(Document), default=list())
    qualified = BooleanType()
    eligible = BooleanType()

    def validate_qualified(self, data, qualified):
        pass

    def validate_eligible(self, data, eligible):
        pass


class Qualification(Model):
    """ Pre-Qualification """

    class Options:
        roles = {
            'create': blacklist('id', 'status', 'documents', 'date'),
            'edit': whitelist('status', 'qualified', 'eligible', 'title', 'title_en', 'title_ru',
                              'description', 'description_en', 'description_ru'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bidID = StringType(required=True)
    lotID = MD5Type()
    status = StringType(choices=['pending', 'active', 'unsuccessful', 'cancelled'], default='pending')
    date = IsoDateTimeType()
    documents = ListType(ModelType(Document), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)

    def validate_qualified(self, data, qualified):
        if data['status'] == 'active' and not qualified:
            raise ValidationError(u'This field is required.')

    def validate_eligible(self, data, eligible):
        if data['status'] == 'active' and not eligible:
            raise ValidationError(u'This field is required.')

    def validate_lotID(self, data, lotID):
        if isinstance(data['__parent__'], Model):
            if not lotID and data['__parent__'].lots:
                raise ValidationError(u'This field is required.')
            if lotID and lotID not in [i.id for i in data['__parent__'].lots]:
                raise ValidationError(u"lotID should be one of lots")


@implementer(ITender)
class Tender(BaseTender):
    """ OpenEU tender model """
    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role_eu,
            'edit': edit_role_eu,
            'edit_draft': edit_role_eu,
            'edit_active.tendering': edit_role_eu,
            'edit_active.pre-qualification': whitelist('status'),
            'edit_active.pre-qualification.stand-still': whitelist(),
            'edit_active.auction': whitelist(),
            'edit_active.qualification': whitelist(),
            'edit_active.awarded': whitelist(),
            'edit_complete': whitelist(),
            'edit_unsuccessful': whitelist(),
            'edit_cancelled': whitelist(),
            'view': view_role,
            'listing': listing_role,
            'auction_view': auction_view_role,
            'auction_post': auction_post_role,
            'auction_patch': auction_patch_role,
            'draft': enquiries_role,
            'active.tendering': enquiries_role,
            'active.pre-qualification': pre_qualifications_role,
            'active.pre-qualification.stand-still': pre_qualifications_role,
            'active.auction': pre_qualifications_role,
            'active.qualification': view_role,
            'active.awarded': view_role,
            'complete': view_role,
            'unsuccessful': view_role,
            'cancelled': view_role,
            'chronograph': chronograph_role,
            'chronograph_view': chronograph_view_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
            'contracting': whitelist('doc_id', 'owner'),
        }

    procurementMethodType = StringType(default="aboveThresholdEU")
    title_en = StringType(required=True, min_length=1)

    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the tender.
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    cancellations = ListType(ModelType(Cancellation), default=list())
    awards = ListType(ModelType(Award), default=list())
    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'invalid.pre-qualification', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    qualifications = ListType(ModelType(Qualification), default=list())
    qualificationPeriod = ModelType(Period)
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction',
                                 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')

    create_accreditation = 3
    edit_accreditation = 4
    procuring_entity_kinds = ['general', 'special', 'defense']
    block_tender_complaint_status = OpenUATender.block_tender_complaint_status
    block_complaint_status = OpenUATender.block_complaint_status

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_qualification_complaint')
            for i in self.bids
            if i.status in ['active', 'unsuccessful']
        ]
        acl.extend([
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
            if i.status == 'active'
        ])
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
        ])
        return acl

    def initialize(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
        self.enquiryPeriod = EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                                endDate=endDate,
                                                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                                clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))
        now = get_now()
        self.date = now
        if self.lots:
            for lot in self.lots:
                lot.date = now

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
        return EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                  endDate=endDate,
                                  invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                  clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        normalized_end = calculate_normalized_date(self.tenderPeriod.endDate, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(normalized_end, -COMPLAINT_SUBMIT_TIME, self)))

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod.endDate and \
                not any([i.status in self.block_tender_complaint_status for i in self.complaints]) and \
                not any([i.id for i in self.questions if not i.answer]):
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif self.status == 'active.pre-qualification.stand-still' and self.qualificationPeriod and self.qualificationPeriod.endDate and not any([
            i.status in self.block_complaint_status
            for q in self.qualifications
            for i in q.complaints
        ]):
            checks.append(self.qualificationPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.auction' and self.auctionPeriod and self.auctionPeriod.startDate and not self.auctionPeriod.endDate:
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ))
        elif self.lots and self.status == 'active.auction':
            for lot in self.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        elif not self.lots and self.status == 'active.awarded' and not any([
                i.status in self.block_complaint_status
                for i in self.complaints
            ]) and not any([
                i.status in self.block_complaint_status
                for a in self.awards
                for i in a.complaints
            ]):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod.endDate
            ]
            last_award_status = self.awards[-1].status if self.awards else ''
            if standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
        elif self.lots and self.status in ['active.qualification', 'active.awarded'] and not any([
                i.status in self.block_complaint_status and i.relatedLot is None
                for i in self.complaints
            ]):
            for lot in self.lots:
                if lot['status'] != 'active':
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                pending_complaints = any([
                    i['status'] in self.block_complaint_status and i.relatedLot == lot.id
                    for i in self.complaints
                ])
                pending_awards_complaints = any([
                    i.status in self.block_complaint_status
                    for a in lot_awards
                    for i in a.complaints
                ])
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod.endDate
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ''
                if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                    checks.append(max(standStillEnds))
        return min(checks).isoformat() if checks else None

    def validate_tenderPeriod(self, data, period):
        # if data['_rev'] is None when tender was created just now
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDERING_DURATION, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status in ("active", "pending",)])

    def check_auction_time(self):
        if self.auctionPeriod and self.auctionPeriod.startDate and self.auctionPeriod.shouldStartAfter \
                and self.auctionPeriod.startDate > calculate_business_date(parse_date(self.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
            self.auctionPeriod.startDate = None
        for lot in self.lots:
            if lot.auctionPeriod and lot.auctionPeriod.startDate and lot.auctionPeriod.shouldStartAfter \
                    and lot.auctionPeriod.startDate > calculate_business_date(parse_date(lot.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
                lot.auctionPeriod.startDate = None

    def invalidate_bids_data(self):
        self.check_auction_time()
        self.enquiryPeriod.invalidationDate = get_now()
        for bid in self.bids:
            if bid.status not in ["deleted", "draft"]:
                bid.status = "invalid"
