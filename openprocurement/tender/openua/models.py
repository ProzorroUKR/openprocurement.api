# -*- coding: utf-8 -*-
from datetime import timedelta, time, datetime
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
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import LotValue as BaseLotValue
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, listing_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, view_bid_role,
    Administrator_bid_role, Administrator_role, schematics_default_role,
    TZ, get_now, schematics_embedded_role, validate_lots_uniq,
    embedded_lot_role, default_lot_role, calc_auction_end_time, get_tender,
    ComplaintModelType,
)
from openprocurement.api.models import ITender
from openprocurement.tender.openua.utils import (
    calculate_business_date, BLOCK_COMPLAINT_STATUS,
)

edit_role_ua = edit_role + blacklist('enquiryPeriod', 'status')


STAND_STILL_TIME = timedelta(days=10)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
CLAIM_SUBMIT_TIME = timedelta(days=10)
COMPLAINT_SUBMIT_TIME = timedelta(days=4)
TENDER_PERIOD = timedelta(days=15)
ENQUIRY_PERIOD_TIME = timedelta(days=10)
TENDERING_EXTRA_PERIOD = timedelta(days=7)


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

class LotValue(BaseLotValue):

    def validate_value(self, data, value):
        if value and isinstance(data['__parent__'], Bid) and ( data['__parent__'].status not in ('invalid')) and data['relatedLot']:
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


class Bid(BaseBid):

    class Options:
        roles = {
            'Administrator': Administrator_bid_role,
            'embedded': view_bid_role,
            'view': view_bid_role,
            'create': whitelist('value', 'tenderers', 'parameters', 'lotValues'),
            'edit': whitelist('value', 'tenderers', 'parameters', 'lotValues', 'status'),
            'auction_view': whitelist('value', 'lotValues', 'id', 'date', 'parameters', 'participationUrl'),
            'auction_post': whitelist('value', 'lotValues', 'id', 'date'),
            'auction_patch': whitelist('id', 'lotValues', 'participationUrl'),
            'active.enquiries': whitelist(),
            'active.tendering': whitelist(),
            'active.auction': whitelist(),
            'active.qualification': view_bid_role,
            'active.awarded': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful': view_bid_role,
            'cancelled': view_bid_role,
            'invalid': whitelist('id', 'status'),
            'deleted': whitelist('id', 'status'),
        }

    lotValues = ListType(ModelType(LotValue), default=list())
    status = StringType(choices=['active', 'invalid', 'deleted'], default='active')

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


class PeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True, default=get_now)  # The state date for the period.
    endDate = IsoDateTimeType(required=True, default=get_now)  # The end date for the period.


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
    status = StringType(choices=['draft', 'claim', 'answered', 'pending', 'accepted', 'invalid', 'resolved', 'declined', 'cancelled', 'satisfied', 'ignored'], default='draft')
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
        elif request.authenticated_role == 'aboveThresholdReviewers' and self.status == 'accepted':
            role = 'review'
        else:
            role = 'invalid'
        return role


class Award(BaseAward):
    complaints = ListType(ModelType(Complaint), default=list())


class Lot(BaseLot):

    class Options:
        roles = {
            'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'minimalStep'),
            'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en', 'description_ru', 'value', 'minimalStep'),
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


@implementer(ITender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role_ua,
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
        }

    __name__ = ''

    enquiryPeriod = ModelType(Period, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    awards = ListType(ModelType(Award), default=list())
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    procurementMethodType = StringType(default="aboveThresholdUA")
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    status = StringType(choices=['active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')

    def validate_tenderPeriod(self, data, period):
        if period and calculate_business_date(period.startDate, TENDER_PERIOD) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than 15 days")

    def initialize(self):
        self.enquiryPeriod = Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME)))

    @serializable(serialized_name="enquiryPeriod", type=ModelType(Period))
    def tender_enquiryPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME)))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME)))

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status == "active"])

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod.endDate and not any([i.status in BLOCK_COMPLAINT_STATUS for i in self.complaints]):
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
        for bid in self.bids:
            if bid.status != "deleted":
                bid.status = "invalid"
