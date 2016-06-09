# -*- coding: utf-8 -*-
from datetime import timedelta, time, datetime
from iso8601 import parse_date
from zope.interface import implementer
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.models import Award as BaseAward
from openprocurement.api.models import Bid as BaseBid
from openprocurement.api.models import Complaint as BaseComplaint
from openprocurement.api.models import ListType
from openprocurement.api.models import Lot as BaseLot
from openprocurement.api.models import Period, IsoDateTimeType
from openprocurement.api.models import Address as BaseAddress
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import LotValue as BaseLotValue
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import Contract as BaseContract
from openprocurement.api.models import Cancellation as BaseCancellation
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, listing_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, view_bid_role,
    Administrator_bid_role, Administrator_role, schematics_default_role,
    TZ, get_now, schematics_embedded_role, validate_lots_uniq, draft_role,
    embedded_lot_role, default_lot_role, calc_auction_end_time, get_tender,
    ComplaintModelType, validate_cpv_group, validate_items_uniq, Model,
)
from openprocurement.api.models import ITender
from openprocurement.tender.openua.utils import (
    calculate_business_date, BLOCK_COMPLAINT_STATUS,
)

edit_role_ua = edit_role + blacklist('enquiryPeriod', 'status')


STAND_STILL_TIME = timedelta(days=10)
ENQUIRY_STAND_STILL_TIME = timedelta(days=3)
CLAIM_SUBMIT_TIME = timedelta(days=10)
COMPLAINT_SUBMIT_TIME = timedelta(days=4)
TENDER_PERIOD = timedelta(days=15)
ENQUIRY_PERIOD_TIME = timedelta(days=10)
TENDERING_EXTRA_PERIOD = timedelta(days=7)
AUCTION_PERIOD_TIME = timedelta(days=2)


def bids_validation_wrapper(validation_func):
    def validator(klass, data, value):
        if data['status'] in ('deleted', 'invalid'):
            # skip not valid bids
            return
        tender = data['__parent__']
        request = tender.__parent__.request
        if request.method == "PATCH" and isinstance(tender, Tender) and request.authenticated_role == "tender_owner":
            # disable bids validation on tender PATCH requests as tender bids will be invalidated
            return
        return validation_func(klass, data, value)
    return validator


class SifterListType(ListType):

    def __init__(self, field, min_size=None, max_size=None,
                 filter_by=None, filter_in_values=[], **kwargs):
        self.filter_by = filter_by
        self.filter_in_values = filter_in_values
        super(SifterListType, self).__init__(field, min_size=min_size,
                                             max_size=max_size, **kwargs)

    def export_loop(self, list_instance, field_converter,
                    role=None, print_none=False):
        """ Use the same functionality as original method but apply
        additional filters.
        """
        data = []
        for value in list_instance:
            if hasattr(self.field, 'export_loop'):
                item_role = role
                # apply filters
                if role not in ['plain', None] and self.filter_by and hasattr(value, self.filter_by):
                    val = getattr(value, self.filter_by)
                    if val in self.filter_in_values:
                        item_role = val

                shaped = self.field.export_loop(value, field_converter,
                                                role=item_role,
                                                print_none=print_none)
                feels_empty = shaped and len(shaped) == 0
            else:
                shaped = field_converter(self.field, value)
                feels_empty = shaped is None

            # Print if we want empty or found a value
            if feels_empty and self.field.allow_none():
                data.append(shaped)
            elif shaped is not None:
                data.append(shaped)
            elif print_none:
                data.append(shaped)

        # Return data if the list contains anything
        if len(data) > 0:
            return data
        elif len(data) == 0 and self.allow_none():
            return data
        elif print_none:
            return data


class TenderAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = self.__parent__
        if tender.lots or tender.status not in ['active.tendering', 'active.auction']:
            return
        if self.startDate and get_now() > calc_auction_end_time(tender.numberOfBids, self.startDate):
            return calc_auction_end_time(tender.numberOfBids, self.startDate).isoformat()
        else:
            decision_dates = [
                datetime.combine(complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo))
                for complaint in tender.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.tenderPeriod.endDate)
            return max(decision_dates).isoformat()


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        if tender.status not in ['active.tendering', 'active.auction'] or lot.status != 'active':
            return
        if self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            return calc_auction_end_time(lot.numberOfBids, self.startDate).isoformat()
        else:
            decision_dates = [
                datetime.combine(complaint.dateDecision.date() + timedelta(days=3), time(0, tzinfo=complaint.dateDecision.tzinfo))
                for complaint in tender.complaints
                if complaint.dateDecision
            ]
            decision_dates.append(tender.tenderPeriod.endDate)
            return max(decision_dates).isoformat()


class PeriodEndRequired(Model):

    startDate = IsoDateTimeType()  # The state date for the period.
    endDate = IsoDateTimeType(required=True)  # The end date for the period.


class PeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True, default=get_now)  # The state date for the period.
    endDate = IsoDateTimeType(required=True, default=get_now)  # The end date for the period.


class EnquiryPeriod(Period):
    clarificationsUntil = IsoDateTimeType()
    invalidationDate = IsoDateTimeType()


class Address(BaseAddress):

    streetAddress = StringType(required=True)
    locality = StringType(required=True)
    region = StringType(required=True)
    postalCode = StringType(required=True)

class Item(BaseItem):
    """A good, service, or work to be contracted."""

    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)

class Contract(BaseContract):

    items = ListType(ModelType(Item))

class LotValue(BaseLotValue):
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'create': whitelist('value', 'relatedLot', 'subcontractingDetails'),
            'edit': whitelist('value', 'relatedLot', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'date', 'relatedLot', 'participationUrl'),
            'auction_post': whitelist('value', 'date', 'relatedLot'),
            'auction_patch': whitelist('participationUrl', 'relatedLot'),
        }
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        if value and isinstance(data['__parent__'], Bid) and ( data['__parent__'].status not in ('invalid', 'deleted')) and data['relatedLot']:
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
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'selfQualified', 'selfEligible', 'subcontractingDetails'),
            'edit': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status', 'subcontractingDetails'),
            'auction_view': whitelist('value', 'lotValues', 'id', 'date', 'parameters', 'participationUrl', 'status'),
            'auction_post': whitelist('value', 'lotValues', 'id', 'date'),
            'auction_patch': whitelist('id', 'lotValues', 'participationUrl'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.auction': whitelist(),
            'active.qualification': view_bid_role,
            'active.awarded': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful':  view_bid_role,
            'cancelled': view_bid_role,
            'invalid': whitelist('id', 'status'),
            'deleted': whitelist('id', 'status'),
        }

    lotValues = ListType(ModelType(LotValue), default=list())
    subcontractingDetails = StringType()
    status = StringType(choices=['active', 'invalid', 'deleted'], default='active')
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(required=True, choices=[True])

    def serialize(self, role=None):
        if role and self.status in ['invalid', 'deleted']:
            role = self.status
        return super(Bid, self).serialize(role)

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

class Complaint(BaseComplaint):
    class Options:
        roles = {
            'create': whitelist('author', 'title', 'description', 'status', 'relatedLot'),
            'draft': whitelist('author', 'title', 'description', 'status'),
            'cancellation': whitelist('cancellationReason', 'status'),
            'satisfy': whitelist('satisfied', 'status'),
            'escalate': whitelist('status'),
            'resolve': whitelist('status', 'tendererAction'),
            'answer': whitelist('resolution', 'resolutionType', 'status', 'tendererAction'),
            'action': whitelist('tendererAction'),
            'pending': whitelist('decision', 'status', 'rejectReason', 'rejectReasonDescription'),
            'review': whitelist('decision', 'status', 'reviewDate', 'reviewPlace'),
            'embedded': (blacklist('owner_token', 'owner') + schematics_embedded_role),
            'view': (blacklist('owner_token', 'owner') + schematics_default_role),
        }
    status = StringType(choices=['draft', 'claim', 'answered', 'pending', 'accepted', 'invalid', 'resolved', 'declined', 'cancelled', 'satisfied', 'stopping', 'stopped'], default='draft')
    acceptance = BooleanType()
    dateAccepted = IsoDateTimeType()
    rejectReason = StringType(choices=['lawNonСompliance', 'noPaymentReceived', 'buyerViolationsСorrected'])
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()

    def __acl__(self):
        return [
            (Allow, 'g:aboveThresholdReviewers', 'edit_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_complaint_documents'),
        ]

    def get_role(self):
        root = self.__parent__
        while root.__parent__ is not None:
            root = root.__parent__
        request = root.request
        data = request.json_body['data']
        if request.authenticated_role == 'complaint_owner' and data.get('status', self.status) == 'cancelled':
            role = 'cancellation'
        elif request.authenticated_role == 'complaint_owner' and self.status in ['pending', 'accepted'] and data.get('status', self.status) == 'stopping':
            role = 'cancellation'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'draft':
            role = 'draft'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'claim':
            role = 'escalate'
        elif request.authenticated_role == 'tender_owner' and self.status == 'claim':
            role = 'answer'
        elif request.authenticated_role == 'tender_owner' and self.status in ['pending', 'accepted']:
            role = 'action'
        elif request.authenticated_role == 'tender_owner' and self.status == 'satisfied':
            role = 'resolve'
        elif request.authenticated_role == 'complaint_owner' and self.status == 'answered':
            role = 'satisfy'
        elif request.authenticated_role == 'aboveThresholdReviewers' and self.status == 'pending':
            role = 'pending'
        elif request.authenticated_role == 'aboveThresholdReviewers' and self.status in ['accepted', 'stopping']:
            role = 'review'
        else:
            role = 'invalid'
        return role

    def validate_cancellationReason(self, data, cancellationReason):
        if not cancellationReason and data.get('status') in ['cancelled', 'stopping']:
            raise ValidationError(u'This field is required.')


class Award(BaseAward):
    class Options:
        roles = {
            'edit': whitelist('status', 'qualified', 'eligible', 'title', 'title_en', 'title_ru',
                              'description', 'description_en', 'description_ru'),
        }
    complaints = ListType(ModelType(Complaint), default=list())
    items = ListType(ModelType(Item))
    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)

    def validate_qualified(self, data, qualified):
        if data['status'] == 'active' and not qualified:
            raise ValidationError(u'This field is required.')

    def validate_eligible(self, data, eligible):
        if data['status'] == 'active' and not eligible:
            raise ValidationError(u'This field is required.')


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
            if self.id in [i.relatedLot for i in bid.lotValues] and bid.status == "active"
        ]
        return len(bids)

class Cancellation(BaseCancellation):
    class Options:
        roles = {
            'create': whitelist('reason', 'status', 'reasonType', 'cancellationOf', 'relatedLot'),
            'edit': whitelist('status', 'reasonType'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    reasonType = StringType(choices=['cancelled', 'unsuccessful'], default='cancelled')

@implementer(ITender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role_ua,
            'edit_draft': draft_role,
            'edit_active.tendering': edit_role_ua,
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
            'active.auction': auction_role,
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

    __name__ = ''

    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    awards = ListType(ModelType(Award), default=list())
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    procurementMethodType = StringType(default="aboveThresholdUA")
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    status = StringType(choices=['draft', 'active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    cancellations = ListType(ModelType(Cancellation), default=list())

    create_accreditation = 3
    edit_accreditation = 4
    procuring_entity_kinds = ['general', 'special', 'defense']

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
            if i.status == 'active'
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
        ])
        return acl

    def validate_tenderPeriod(self, data, period):
        # if data['_rev'] is None when tender was created just now
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDER_PERIOD, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than 15 days")

    def initialize(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self)
        self.enquiryPeriod = EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                                endDate=endDate,
                                                invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                                clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self)
        return EnquiryPeriod(dict(startDate=self.tenderPeriod.startDate,
                                  endDate=endDate,
                                  invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
                                  clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)))

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status == "active"])

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod.endDate and \
            not any([i.status in BLOCK_COMPLAINT_STATUS for i in self.complaints]) and \
            not any([i.id for i in self.questions if not i.answer]):
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
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
        elif not self.lots and self.status == 'active.awarded':
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod.endDate
            ]
            if standStillEnds:
                standStillEnd = max(standStillEnds)
                if standStillEnd > now:
                    checks.append(standStillEnd)
        elif self.lots and self.status in ['active.qualification', 'active.awarded']:
            lots_ends = []
            for lot in self.lots:
                if lot['status'] != 'active':
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod.endDate
                ]
                if not standStillEnds:
                    continue
                standStillEnd = max(standStillEnds)
                if standStillEnd > now:
                    lots_ends.append(standStillEnd)
            if lots_ends:
                checks.append(min(lots_ends))
        return min(checks).isoformat() if checks else None

    def invalidate_bids_data(self):
        if self.auctionPeriod and self.auctionPeriod.startDate and self.auctionPeriod.shouldStartAfter \
                and self.auctionPeriod.startDate > calculate_business_date(parse_date(self.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
            self.auctionPeriod.startDate = None
        for lot in self.lots:
            if lot.auctionPeriod and lot.auctionPeriod.startDate and lot.auctionPeriod.shouldStartAfter \
                    and lot.auctionPeriod.startDate > calculate_business_date(parse_date(lot.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
                lot.auctionPeriod.startDate = None
        self.enquiryPeriod.invalidationDate = get_now()
        for bid in self.bids:
            if bid.status != "deleted":
                bid.status = "invalid"
