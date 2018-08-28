# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.submodels.agreement import Agreement
from openprocurement.tender.cfaselectionua.models.submodels.award import Award
from openprocurement.tender.cfaselectionua.models.submodels.contract import Contract
from openprocurement.tender.cfaselectionua.models.submodels.lot import Lot
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from schematics.types import StringType, IntType, URLType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from barbecue import vnmax
from zope.interface import implementer
from pyramid.security import Allow
from openprocurement.api.models import schematics_embedded_role
from openprocurement.api.models import ListType, Period, Value
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ
from openprocurement.api.validation import validate_items_uniq, validate_cpv_group
from openprocurement.tender.core.models import (
    validate_features_uniq, validate_lots_uniq,
    create_role as base_create_role, edit_role as base_edit_role,
    Guarantee, TenderAuctionPeriod,
    PeriodEndRequired, Tender as BaseTender, Bid, ProcuringEntity,
    Item, Cancellation, Feature
)
from openprocurement.tender.core.utils import calc_auction_end_time
from openprocurement.tender.cfaselectionua.constants import BOT_NAME, DRAFT_FIELDS


enquiries_role = (blacklist('owner_token', '_attachments', 'revisions', 'bids', 'numberOfBids') + schematics_embedded_role)
edit_role = (blacklist(*DRAFT_FIELDS) + base_edit_role)
create_role = (blacklist(*DRAFT_FIELDS) + base_create_role)
Administrator_role = whitelist('status', 'mode', 'procuringEntity', 'auctionPeriod', 'lots')


@implementer(ICFASelectionUATender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """
    class Options:
        roles = RolesFromCsv('Tender.csv', relative_to=__file__)

    items = ListType(ModelType(Item), min_size=1, validators=[validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    enquiryPeriod = ModelType(PeriodEndRequired, required=True)  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(PeriodEndRequired, required=True)  # The period when the tender is open for submissions. The end date is the closing date for tender submissions.
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    awardPeriod = ModelType(Period)  # The date or period on which an award is anticipated to be made.
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the tender.
    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    minimalStep = ModelType(Value, required=True)
    auctionUrl = URLType()
    cancellations = ListType(ModelType(Cancellation), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq], min_size=1, max_size=1)
    guarantee = ModelType(Guarantee)
    status = StringType(choices=['draft', 'draft.pending', 'draft.unsuccessful', 'active.enquiries', 'active.tendering',
                                 'active.auction', 'active.qualification', 'active.awarded', 'complete',
                                 'cancelled', 'unsuccessful'], default='draft.pending')  # TODO Refactoring status
    agreements = ListType(ModelType(Agreement), default=list())

    procurementMethod = StringType(choices=['open', 'selective', 'limited'], default='selective')
    procurementMethodType = StringType(default="closeFrameworkAgreementSelectionUA")
    procuring_entity_kinds = ['general', 'special', 'defense', 'other']

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == 'Administrator':
            role = 'Administrator'
        elif request.authenticated_role == 'chronograph':
            role = 'chronograph'
        elif request.authenticated_role == 'auction':
            role = 'auction_{}'.format(request.method.lower())
        elif request.authenticated_role == 'contracting':
            role = 'contracting'
        elif request.authenticated_role == 'agreement_selection':
            role = 'edit_{}'.format(request.authenticated_role)
        else:
            role = 'edit_{}'.format(request.context.status)
        return role

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
        ]
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
            (Allow, 'g:agreement_selection', 'edit_agreement_selection'),
            (Allow, 'g:agreement_selection', 'edit_tender'),
        ])
        return acl

    def __local_roles__(self):
        roles = dict([('{}_{}'.format(self.owner, self.owner_token), 'tender_owner')])
        for i in self.bids:
            roles['{}_{}'.format(i.owner, i.owner_token)] = 'bid_owner'
        return roles

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.enquiries' and self.tenderPeriod.startDate:
            checks.append(self.tenderPeriod.startDate.astimezone(TZ))
        elif self.status == 'active.enquiries' and self.enquiryPeriod.endDate:
            checks.append(self.enquiryPeriod.endDate.astimezone(TZ))
        elif self.status == 'active.tendering' and self.tenderPeriod.endDate:
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
        elif self.lots and self.status in ['active.qualification', 'active.awarded']:
            for lot in self.lots:
                if lot['status'] != 'active':
                    continue
        if self.status.startswith('active'):
            for award in self.awards:
                if award.status == 'active' and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)
        return min(checks).isoformat() if checks else None

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len(self.bids)

    @serializable(serialized_name="value", type=ModelType(Value))
    def tender_value(self):
        return Value(dict(amount=sum([i.value.amount for i in self.lots]),
                          currency=self.value.currency,
                          valueAddedTaxIncluded=self.value.valueAddedTaxIncluded)) if self.lots else self.value

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {'amount': sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee['currency'] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee['currency'] = self.guarantee.currency
            return Guarantee(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def tender_minimalStep(self):
        return Value(dict(amount=min([i.minimalStep.amount for i in self.lots]),
                          currency=self.minimalStep.currency,
                          valueAddedTaxIncluded=self.minimalStep.valueAddedTaxIncluded)) if self.lots else self.minimalStep

    def validate_items(self, data, items):
        cpv_336_group = items[0].classification.id[:3] == '336' if items else False
        if not cpv_336_group and items and len(set([i.classification.id[:4] for i in items])) != 1:
            raise ValidationError(u"CPV class of items should be identical")
        else:
            validate_cpv_group(items)

    def validate_features(self, data, features):
        if features and data['lots'] and any([
            round(vnmax([
                i
                for i in features
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot['id'] or i.featureOf == 'item' and i.relatedItem in [j.id for j in data['items'] if j.relatedLot == lot['id']]
            ]), 15) > 0.3
            for lot in data['lots']
        ]):
            raise ValidationError(u"Sum of max value of all features for lot should be less then or equal to 30%")
        elif features and not data['lots'] and round(vnmax(features), 15) > 0.3:
            raise ValidationError(u"Sum of max value of all features should be less then or equal to 30%")

    def validate_auctionUrl(self, data, url):
        if url and data['lots']:
            raise ValidationError(u"url should be posted for each lot")

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get('value'):
            if data.get('value').amount < value.amount:
                raise ValidationError(u"value should be less than value of tender")
            if data.get('value').currency != value.currency:
                raise ValidationError(u"currency should be identical to currency of value of tender")
            if data.get('value').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender")

    def validate_tenderPeriod(self, data, period):
        if period and period.startDate and data.get('enquiryPeriod') and data.get('enquiryPeriod').endDate and period.startDate < data.get('enquiryPeriod').endDate:
            raise ValidationError(u"period should begin after enquiryPeriod")

    def validate_awardPeriod(self, data, period):
        if period and period.startDate and data.get('auctionPeriod') and data.get('auctionPeriod').endDate and period.startDate < data.get('auctionPeriod').endDate:
            raise ValidationError(u"period should begin after auctionPeriod")
        if period and period.startDate and data.get('tenderPeriod') and data.get('tenderPeriod').endDate and period.startDate < data.get('tenderPeriod').endDate:
            raise ValidationError(u"period should begin after tenderPeriod")

    def validate_lots(self, data, value):
        if len(set([lot.guarantee.currency for lot in value if lot.guarantee])) > 1:
            raise ValidationError(u"lot guarantee currency should be identical to tender guarantee currency")
