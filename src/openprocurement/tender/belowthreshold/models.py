# -*- coding: utf-8 -*-
from datetime import timedelta

from pyramid.security import Allow

from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types import StringType, IntType, URLType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from barbecue import vnmax
from zope.interface import implementer

from openprocurement.api.models import ListType, Period, Value, Guarantee
from openprocurement.api.utils import get_now, get_first_revision_date
from openprocurement.api.constants import TZ, RELEASE_2020_04_19, CPV_ITEMS_CLASS_FROM
from openprocurement.api.validation import validate_items_uniq, validate_cpv_group, validate_classification_id
from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME
from openprocurement.tender.core.validation import validate_minimalstep

from openprocurement.tender.core.models import (
    ITender,
    ComplaintModelType,
    TenderAuctionPeriod,
    PeriodEndRequired,
    Tender as BaseTender,
    Bid as BaseBid,
    ProcuringEntity,
    Item,
    Award,
    Contract,
    Question,
    Cancellation as BaseCancellation,
    Feature,
    LotWithMinimalStepLimitsValidation as BaseLot,
    Complaint,
    BidResponsesMixin,
    validate_features_uniq,
    validate_lots_uniq,
    get_tender
)

from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    normalize_should_start_after,
    calculate_tender_date,
    calculate_tender_business_date,
)
from openprocurement.tender.openua.validation import validate_tender_period_duration


class LotAuctionPeriod(Period):
    """The auction period."""

    @serializable(serialize_when_none=False)
    def shouldStartAfter(self):
        if self.endDate:
            return
        tender = get_tender(self)
        lot = self.__parent__
        statuses = ["active.tendering", "active.auction"]
        if tender.status not in statuses or lot.status != "active":
            return
        if tender.status == "active.auction" and lot.numberOfBids < 2:
            return
        if self.startDate and get_now() > calc_auction_end_time(lot.numberOfBids, self.startDate):
            start_after = calc_auction_end_time(tender.numberOfBids, self.startDate)
        else:
            start_after = tender.tenderPeriod.endDate
        return normalize_should_start_after(start_after, tender).isoformat()


class Lot(BaseLot):
    auctionPeriod = ModelType(LotAuctionPeriod, default={})


class IBelowThresholdTender(ITender):
    """ Marker interface for belowThreshold tenders """


class Cancellation(BaseCancellation):
    _before_release_reasonType_choices = []
    _after_release_reasonType_choices = ["noDemand", "unFixable", "expensesCut"]

    _after_release_status_choices = ["draft", "unsuccessful", "active"]


class Bid(BaseBid, BidResponsesMixin):
    pass


@implementer(IBelowThresholdTender)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        namespace = "Tender"
        _core_roles = BaseTender.Options.roles
        # without _serializable_fields they won't be calculated (even though serialized_name is in the role)
        _serializable_fields = whitelist("tender_guarantee", "tender_value", "tender_minimalStep")
        _edit_fields = _serializable_fields + whitelist(
            "enquiryPeriod",
            "next_check",
            "numberOfBidders",
            "hasEnquiries",
            "features",
            "items",
            "tenderPeriod",
            "procuringEntity",
            "guarantee",
            "value",
            "minimalStep",
        )
        _edit_role = _core_roles["edit"] + _edit_fields + whitelist("contracts", "numberOfBids")
        _view_tendering_role = (
            _core_roles["view"]
            + _edit_fields
            + whitelist(
                "auctionUrl",
                "awards",
                "awardPeriod",
                "questions",
                "lots",
                "cancellations",
                "complaints",
                "contracts",
                "auctionPeriod",
            )
        )
        _view_role = _view_tendering_role + whitelist("bids", "numberOfBids")
        _all_forbidden = whitelist()
        roles = {
            "create": _core_roles["create"] + _edit_role + whitelist("lots"),
            "edit": _edit_role,
            "edit_draft": _core_roles["edit_draft"],
            "edit_active.enquiries": _edit_role,
            "edit_active.tendering": _all_forbidden,
            "edit_active.auction": _all_forbidden,
            "edit_active.qualification": _all_forbidden,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "draft": _view_tendering_role,
            "active.enquiries": _view_tendering_role,
            "active.tendering": _view_tendering_role,
            "active.auction": _view_tendering_role,
            "view": _view_role,
            "active.qualification": _view_role,
            "active.awarded": _view_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "auction_view": _core_roles["auction_view"],
            "auction_post": _core_roles["auction_post"],
            "auction_patch": _core_roles["auction_patch"],
            "chronograph": _core_roles["chronograph"],
            "chronograph_view": _core_roles["chronograph_view"],
            "Administrator": _core_roles["Administrator"],
            "plain": _core_roles["plain"],
            "listing": _core_roles["listing"],
            "contracting": _core_roles["contracting"],
            "default": _core_roles["default"],
        }

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    enquiryPeriod = ModelType(
        PeriodEndRequired, required=True
    )  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(
        PeriodEndRequired, required=True
    )  # The period when the tender is open for submissions. The end date is the closing date for tender submissions.
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    awardPeriod = ModelType(Period)  # The date or period on which an award is anticipated to be made.
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    bids = ListType(
        ModelType(Bid, required=True), default=list()
    )  # A list of all the companies who entered submissions for the tender.
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    minimalStep = ModelType(Value, required=True)
    questions = ListType(ModelType(Question, required=True), default=list())
    complaints = ListType(ComplaintModelType(Complaint, required=True), default=list())
    auctionUrl = URLType()
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq])
    guarantee = ModelType(Guarantee)

    procurementMethodType = StringType(default="belowThreshold")

    procuring_entity_kinds = ["authority", "central", "defense", "general", "other", "social", "special"]
    block_complaint_status = ["answered", "pending"]

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "tender_owner")])
        for i in self.bids:
            roles["{}_{}".format(i.owner, i.owner_token)] = "bid_owner"
        return roles

    def __acl__(self):
        acl = super(Tender, self).__acl__()
        acl.extend([(Allow, "g:brokers", "create_cancellation_complaint")])
        return acl

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == "active.enquiries" and self.tenderPeriod.startDate:
            checks.append(self.tenderPeriod.startDate.astimezone(TZ))
        elif self.status == "active.enquiries" and self.enquiryPeriod.endDate:
            checks.append(self.enquiryPeriod.endDate.astimezone(TZ))
        elif self.status == "active.tendering" and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif (
            not self.lots
            and self.status == "active.auction"
            and self.auctionPeriod
            and self.auctionPeriod.startDate
            and not self.auctionPeriod.endDate
        ):
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            else:
                auction_end_time = calc_auction_end_time(
                    self.numberOfBids, self.auctionPeriod.startDate
                ).astimezone(TZ)
                if now < auction_end_time:
                    checks.append(auction_end_time)
        elif self.lots and self.status == "active.auction":
            for lot in self.lots:
                if (
                    lot.status != "active"
                    or not lot.auctionPeriod
                    or not lot.auctionPeriod.startDate
                    or lot.auctionPeriod.endDate
                ):
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                else:
                    auction_end_time = calc_auction_end_time(
                        lot.numberOfBids, lot.auctionPeriod.startDate
                    ).astimezone(TZ)
                    if now < auction_end_time:
                        checks.append(auction_end_time)
        elif (
            not self.lots
            and self.status == "active.awarded"
            and not any([i.status in self.block_complaint_status for i in self.complaints])
            and not any([i.status in self.block_complaint_status for a in self.awards for i in a.complaints])
        ):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod and a.complaintPeriod.endDate
            ]
            last_award_status = self.awards[-1].status if self.awards else ""
            if standStillEnds and last_award_status == "unsuccessful":
                checks.append(max(standStillEnds))
        elif (
            self.lots
            and self.status in ["active.qualification", "active.awarded"]
            and not any([i.status in self.block_complaint_status and i.relatedLot is None for i in self.complaints])
        ):
            for lot in self.lots:
                if lot["status"] != "active":
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                pending_complaints = any(
                    [i["status"] in self.block_complaint_status and i.relatedLot == lot.id for i in self.complaints]
                )
                pending_awards_complaints = any(
                    [i.status in self.block_complaint_status for a in lot_awards for i in a.complaints]
                )
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod and a.complaintPeriod.endDate
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ""
                if (
                    not pending_complaints
                    and not pending_awards_complaints
                    and standStillEnds
                    and last_award_status == "unsuccessful"
                ):
                    checks.append(max(standStillEnds))
        if self.status.startswith("active"):
            for complaint in self.complaints:
                if complaint.status == "answered" and complaint.dateAnswered:
                    check = calculate_tender_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self)
                    checks.append(check)
                elif complaint.status == "pending":
                    checks.append(self.dateModified)
            for award in self.awards:
                if award.status == "active" and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)
                for complaint in award.complaints:
                    if complaint.status == "answered" and complaint.dateAnswered:
                        check = calculate_tender_date(complaint.dateAnswered, COMPLAINT_STAND_STILL_TIME, self)
                        checks.append(check)
                    elif complaint.status == "pending":
                        checks.append(self.dateModified)
        return min(checks).isoformat() if checks else None

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len(self.bids)

    @serializable(serialized_name="value", type=ModelType(Value))
    def tender_value(self):
        return (
            Value(
                dict(
                    amount=sum([i.value.amount for i in self.lots]),
                    currency=self.value.currency,
                    valueAddedTaxIncluded=self.value.valueAddedTaxIncluded,
                )
            )
            if self.lots
            else self.value
        )

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {"amount": sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee["currency"] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee["currency"] = self.guarantee.currency
            return Guarantee(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def tender_minimalStep(self):
        return (
            Value(
                dict(
                    amount=min([i.minimalStep.amount for i in self.lots]),
                    currency=self.minimalStep.currency,
                    valueAddedTaxIncluded=self.minimalStep.valueAddedTaxIncluded,
                )
            )
            if self.lots
            else self.minimalStep
        )

    def validate_items(self, data, items):
        cpv_336_group = items[0].classification.id[:3] == "336" if items else False
        if (
            not cpv_336_group
            and (data.get("revisions")[0].date if data.get("revisions") else get_now()) > CPV_ITEMS_CLASS_FROM
            and items
            and len(set([i.classification.id[:4] for i in items])) != 1
        ):
            raise ValidationError(u"CPV class of items should be identical")
        else:
            validate_cpv_group(items)

    def validate_features(self, data, features):
        if (
            features
            and data["lots"]
            and any(
                [
                    round(
                        vnmax(
                            [
                                i
                                for i in features
                                if i.featureOf == "tenderer"
                                or i.featureOf == "lot"
                                and i.relatedItem == lot["id"]
                                or i.featureOf == "item"
                                and i.relatedItem in [j.id for j in data["items"] if j.relatedLot == lot["id"]]
                            ]
                        ),
                        15,
                    )
                    > 0.3
                    for lot in data["lots"]
                ]
            )
        ):
            raise ValidationError(u"Sum of max value of all features for lot should be less then or equal to 30%")
        elif features and not data["lots"] and round(vnmax(features), 15) > 0.3:
            raise ValidationError(u"Sum of max value of all features should be less then or equal to 30%")

    def validate_auctionUrl(self, data, url):
        if url and data["lots"]:
            raise ValidationError(u"url should be posted for each lot")

    def validate_minimalStep(self, data, value):
        validate_minimalstep(data, value)

    def validate_enquiryPeriod(self, data, period):
        active_validation = get_first_revision_date(data, default=get_now()) > RELEASE_2020_04_19

        if (
            active_validation
            and period
            and period.startDate
            and period.endDate
            and period.endDate < calculate_tender_business_date(period.startDate, timedelta(days=3), data, True)
        ):
            raise ValidationError(u"the enquiryPeriod cannot end earlier than 3 business days after the start")

    def validate_tenderPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("enquiryPeriod")
            and data.get("enquiryPeriod").endDate
            and period.startDate < data.get("enquiryPeriod").endDate
        ):
            raise ValidationError(u"period should begin after enquiryPeriod")

        active_validation = get_first_revision_date(data, default=get_now()) > RELEASE_2020_04_19
        if (
            active_validation
            and period
            and period.startDate
            and period.endDate
        ):
            validate_tender_period_duration(data, period, timedelta(days=2), working_days=True)

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("auctionPeriod")
            and data.get("auctionPeriod").endDate
            and period.startDate < data.get("auctionPeriod").endDate
        ):
            raise ValidationError(u"period should begin after auctionPeriod")
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError(u"period should begin after tenderPeriod")

    def validate_lots(self, data, value):
        if len(set([lot.guarantee.currency for lot in value if lot.guarantee])) > 1:
            raise ValidationError(u"lot guarantee currency should be identical to tender guarantee currency")
