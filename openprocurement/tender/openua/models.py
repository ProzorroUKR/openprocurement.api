# -*- coding: utf-8 -*-
from datetime import timedelta
from zope.interface import implementer
from schematics.types import IntType, StringType, BooleanType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist, blacklist
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import Bid as BaseBid
from openprocurement.api.models import Period, IsoDateTimeType
from openprocurement.api.models import Complaint as BaseComplaint
from openprocurement.api.models import Award as BaseAward
from openprocurement.api.models import Lot as BaseLot
from openprocurement.api.models import ListType
from openprocurement.api.models import (
    plain_role, create_role, edit_role, cancel_role, view_role, listing_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, view_bid_role,
    Administrator_bid_role, Administrator_role, schematics_default_role,
    TZ, get_now, schematics_embedded_role, validate_lots_uniq
)
from openprocurement.tender.openua.interfaces import ITenderUA
from schematics.exceptions import ValidationError
from openprocurement.tender.openua.utils import calculate_business_date
from schematics.types.serializable import serializable
from openprocurement.api.models import embedded_lot_role, default_lot_role

edit_role_ua = edit_role + blacklist('enquiryPeriod')


STAND_STILL_TIME = timedelta(days=10)
COMPLAINT_STAND_STILL_TIME = timedelta(days=3)
CLAIM_SUBMIT_TIME = timedelta(days=10)
COMPLAINT_SUBMIT_TIME = timedelta(days=4)
TENDER_PERIOD = timedelta(days=15)
ENQUIRY_PERIOD_TIME = timedelta(days=3)


def bids_validation_wrapper(validation_func):
    def validator(klass, data, value):
        if data['status'] in ('deleted', 'invalid'):
            # skip not valid bids
            return
        tender = data['__parent__']
        request = tender.__parent__.request
        if request.method == "PATCH" and ITenderUA.providedBy(request.context) and request.authenticated_role == "tender_owner":
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
            'answer': whitelist('resolution', 'resolutionType', 'status', 'tendererAction'),
            'action': whitelist('tendererAction'),
            'pending': whitelist('decision', 'status', 'acceptance', 'rejectReason', 'rejectReasonDescription'),
            'review': whitelist('decision', 'status', 'reviewDate', 'reviewPlace'),
            'embedded': (blacklist('owner_token', 'owner') + schematics_embedded_role),
            'view': (blacklist('owner_token', 'owner') + schematics_default_role),
        }
    status = StringType(choices=['draft', 'claim', 'answered', 'pending', 'accepted', 'invalid', 'resolved', 'declined', 'cancelled'], default='draft')
    acceptance = BooleanType()
    rejectReason = StringType(choices=['invalid'])
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()

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
        elif request.authenticated_role == 'complaint_owner' and self.status == 'answered':
            role = 'satisfy'
        elif request.authenticated_role == 'reviewers' and self.status == 'pending':
            role = 'pending'
        elif request.authenticated_role == 'reviewers' and self.status == 'accepted':
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

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues] and bid.status == "active"
        ]
        return len(bids)


@implementer(ITenderUA)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role,
            'edit': edit_role_ua,
            'edit_active.tendering': edit_role_ua,
            'edit_active.auction': cancel_role,
            'edit_active.qualification': cancel_role,
            'edit_active.awarded': cancel_role,
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
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    awards = ListType(ModelType(Award), default=list())
    complaints = ListType(ModelType(Complaint), default=list())
    procurementMethodType = StringType(default="aboveThresholdUA")
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    status = StringType(choices=['active.tendering', 'active.auction', 'active.qualification', 'active.awarded', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')

    def validate_tenderPeriod(self, data, period):
        if period and calculate_business_date(period.startDate, TENDER_PERIOD) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than 15 days")

    def initialize(self):
        if not self.tenderPeriod.startDate:
            self.tenderPeriod.startDate = get_now()
        self.enquiryPeriod = Period(dict(startDate=self.tenderPeriod.startDate, endDate=calculate_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME)))
        if hasattr(self, "auctionPeriod") and hasattr(self.auctionPeriod, "startDate"):
            self.auctionPeriod.startDate = ""

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

    @serializable
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod.endDate and not any([i.status in ['pending', 'accepted'] for i in self.complaints]):
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
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
        return sorted(checks)[0].isoformat() if checks else None

    def invalidate_bids_data(self):
        for bid in self.bids:
            if bid.status != "deleted":
                bid.status = "invalid"