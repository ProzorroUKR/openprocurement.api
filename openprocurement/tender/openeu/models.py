from uuid import uuid4
from datetime import timedelta
from zope.interface import implementer
from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.transforms import blacklist, whitelist
from schematics.exceptions import ValidationError
from openprocurement.api.models import ITender, TZ
from openprocurement.api.models import (Document, Model, Address, Period,
                                        IsoDateTimeType, ListType)
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import Identifier as BaseIdentifier
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import Bid as BaseBid
from openprocurement.api.models import Award as BaseAward
from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.models import validate_cpv_group, validate_items_uniq
from openprocurement.api.models import (
    plain_role, create_role, edit_role, view_role, listing_role,
    auction_view_role, auction_post_role, auction_patch_role, enquiries_role,
    auction_role, chronograph_role, chronograph_view_role, view_bid_role,
    Administrator_bid_role, Administrator_role, schematics_default_role,
    schematics_embedded_role, get_now)
from openprocurement.tender.openua.utils import calculate_business_date
from openprocurement.tender.openua.models import PeriodStartEndRequired, SifterListType

eu_role = blacklist('enquiryPeriod', 'qualifications')
edit_role_eu = edit_role + eu_role
create_role_eu = create_role + eu_role
qualifications_role = enquiries_role + eu_role
eu_auction_role = auction_role + eu_role

TENDERING_DAYS = 30
TENDERING_DURATION = timedelta(days=TENDERING_DAYS)
QUESTIONS_STAND_STILL = timedelta(days=3)
COMPLAINT_STAND_STILL = timedelta(days=10)


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

class Item(BaseItem):
    """A good, service, or work to be contracted."""

    description_en = StringType(required=True, min_length=1)


class Identifier(BaseIdentifier):

    legalName_en = StringType(required=True, min_length=1)


class ContactPoint(BaseContactPoint):

    name_en = StringType(required=True, min_length=1)
    availableLanguage = StringType(required=True, min_length=1)


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
            'active.pre-qualification': enquiries_role,
            'active.pre-qualification.stand-still': enquiries_role,
            'active.auction': whitelist(),
            'active.qualification': view_bid_role,
            'active.awarded': view_bid_role,
            'complete': view_bid_role,
            'unsuccessful': view_bid_role,
            'cancelled': view_bid_role,
            'invalid': whitelist('id', 'status'),
            'deleted': whitelist('id', 'status'),
        }
    status = StringType(choices=['pending', 'active', 'invalid', 'deleted'],
                        default='pending')

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

class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    items = ListType(ModelType(Item))


class Qualification(Model):
    """ Pre-Qualification """

    class Options:
        roles = {
            'create': blacklist('id', 'status', 'documents', 'date'),
            'edit': blacklist('id', 'documents'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    bidID = StringType(required=True)
    status = StringType(choices=['pending', 'active', 'cancelled'], default='pending')
    date = IsoDateTimeType()
    documents = ListType(ModelType(Document), default=list())


@implementer(ITender)
class Tender(BaseTender):
    """ OpenEU tender model """
    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role_eu,
            'edit': edit_role_eu,
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
            'active.tendering': qualifications_role,
            'active.pre-qualification': qualifications_role,
            'active.pre-qualification.stand-still': qualifications_role,
            'active.auction': eu_auction_role,
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

    procurementMethodType = StringType(default="aboveThresholdEU")
    title_en = StringType(required=True, min_length=1)

    enquiryPeriod = ModelType(Period, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    items = ListType(ModelType(Item), required=True, min_size=1, validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    awards = ListType(ModelType(Award), default=list())
    procuringEntity = ModelType(Organization, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    # bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the tender.
    bids = SifterListType(ModelType(Bid), default=list(), filter_by='status', filter_in_values=['invalid', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    qualifications = ListType(ModelType(Qualification), default=list())
    qualificationPeriod = ModelType(Period)
    status = StringType(choices=['active.tendering', 'active.pre-qualification', 'active.pre-qualification.stand-still', 'active.auction',
                                 'active.awarded', 'active.qualification', 'complete', 'cancelled', 'unsuccessful'], default='active.tendering')

    def initialize(self):
        if not self.tenderPeriod.startDate:
            self.tenderPeriod.startDate = get_now()
        self.enquiryPeriod = Period(self.tenderPeriod.to_native())
        self.enquiryPeriod.endDate = calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL)
        if hasattr(self, "auctionPeriod") and hasattr(self.auctionPeriod, "startDate"):
            self.auctionPeriod.startDate = ""

    @serializable(serialized_name="enquiryPeriod", type=ModelType(Period))
    def tender_enquiryPeriod(self):
        return Period(dict(startDate=self.tenderPeriod.startDate,
                           endDate=calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL)))

    @serializable
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif self.status == 'active.pre-qualification.stand-still' and self.qualificationPeriod and self.qualificationPeriod.endDate:
            checks.append(self.qualificationPeriod.endDate.astimezone(TZ))
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
        # TODO: fix Lots functionality
        # elif self.lots and self.status in ['active.qualification', 'active.awarded']:
        #     lots_ends = []
        #     for lot in self.lots:
        #         if lot['status'] != 'active':
        #             continue
        #         lot_awards = [i for i in self.awards if i.lotID == lot.id]
        #         standStillEnds = [
        #             a.complaintPeriod.endDate.astimezone(TZ)
        #             for a in lot_awards
        #             if a.complaintPeriod.endDate
        #         ]
        #         if not standStillEnds:
        #             continue
        #         standStillEnd = max(standStillEnds)
        #         if standStillEnd > now:
        #             lots_ends.append(standStillEnd)
        #     if lots_ends:
        #         checks.append(min(lots_ends))
        for complaint in self.complaints:
            if complaint.status == 'claim' and complaint.dateSubmitted:
                checks.append(complaint.dateSubmitted + COMPLAINT_STAND_STILL)
            elif complaint.status == 'answered' and complaint.dateAnswered:
                checks.append(complaint.dateAnswered + COMPLAINT_STAND_STILL)
        for award in self.awards:
            for complaint in award.complaints:
                if complaint.status == 'claim' and complaint.dateSubmitted:
                    checks.append(complaint.dateSubmitted + COMPLAINT_STAND_STILL)
                elif complaint.status == 'answered' and complaint.dateAnswered:
                    checks.append(complaint.dateAnswered + COMPLAINT_STAND_STILL)
        return sorted(checks)[0].isoformat() if checks else None

    def validate_tenderPeriod(self, data, period):
        if period and calculate_business_date(period.startDate, TENDERING_DURATION) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status in ("active", "pending",)])

    def invalidate_bids_data(self):
        for bid in self.bids:
            if bid.status != "deleted":
                bid.status = "invalid"