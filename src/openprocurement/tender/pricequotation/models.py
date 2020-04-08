# -*- coding: utf-8 -*-
from datetime import timedelta

from barbecue import vnmax
from openprocurement.api.constants import TZ
from openprocurement.api.models import BusinessOrganization, CPVClassification, Guarantee
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import ListType, Period, Value
from openprocurement.api.utils import get_now
from openprocurement.api.validation import validate_classification_id, validate_cpv_group, validate_items_uniq
from openprocurement.tender.core.constants import COMPLAINT_STAND_STILL_TIME, CPV_ITEMS_CLASS_FROM
from openprocurement.tender.core.models import (Award, BaseLot, Bid, Cancellation, Complaint, ComplaintModelType,
                                                Contract, Feature, Item, PeriodEndRequired, ProcuringEntity, Question,
                                                Tender, default_lot_role, embedded_lot_role, validate_features_uniq,
                                                validate_lots_uniq)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.validation import validate_minimalstep
from openprocurement.tender.pricequotation.constants import PMT
from openprocurement.tender.pricequotation.interfaces import IPriceQuotationTender
from pyramid.security import Allow
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from schematics.types import IntType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from zope.interface import implementer


class Lot(BaseLot):
    class Options:
        roles = {
            "create": whitelist(
                "id",
                "title",
                "title_en",
                "title_ru",
                "description",
                "description_en",
                "description_ru",
                "value",
                "guarantee",
                "minimalStep",
            ),
            "edit": whitelist(
                "title",
                "title_en",
                "title_ru",
                "description",
                "description_en",
                "description_ru",
                "value",
                "guarantee",
                "minimalStep",
            ),
            "embedded": embedded_lot_role,
            "view": default_lot_role,
            "default": default_lot_role,
            "auction_view": default_lot_role,
            "auction_patch": whitelist("id", "auctionUrl"),
            "chronograph": whitelist("id", "auctionPeriod"),
            "chronograph_view": whitelist("id", "auctionPeriod", "numberOfBids", "status"),
            "Administrator": whitelist("auctionPeriod"),
        }

    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee)

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues] and getattr(bid, "status", "active") == "active"
        ]
        return len(bids)

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def lot_minimalStep(self):
        return Value(
            dict(
                amount=self.minimalStep.amount,
                currency=self.__parent__.minimalStep.currency,
                valueAddedTaxIncluded=self.__parent__.minimalStep.valueAddedTaxIncluded,
            )
        )

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        return Value(
            dict(
                amount=self.value.amount,
                currency=self.__parent__.value.currency,
                valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded,
            )
        )

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get("value"):
            if data.get("value").amount < value.amount:
                raise ValidationError(u"value should be less than value of lot")


class ShortlistedFirm(BusinessOrganization):
    id = StringType()
    status = StringType()


class Item(BaseItem):
    """A good, service, or work to be contracted."""

    classification = ModelType(CPVClassification)



@implementer(IPriceQuotationTender)
class PriceQuotationTender(Tender):
    # TODO: submissionMethod
    """
    Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        namespace = "Tender"
        _core_roles = Tender.Options.roles
        # without _serializable_fields they won't be calculated
        # (even though serialized_name is in the role)
        _serializable_fields = whitelist(
            "tender_guarantee",
            "tender_value",
            "tender_minimalStep"
        )
        _edit_fields = _serializable_fields + whitelist(
            "next_check",
            "numberOfBidders",
            "features",
            "items",
            "tenderPeriod",
            "procuringEntity",
            "guarantee",
            "value",
            "minimalStep",
        )
        _edit_role = _core_roles["edit"] \
            + _edit_fields + whitelist("contracts", "numberOfBids", "status", "profile")
        _edit_pq_bot_role = whitelist("items", "shortlistedFirms", "status")
        _view_tendering_role = (
            _core_roles["view"]
            + _edit_fields
            + whitelist(
                "awards",
                "awardPeriod",
                "questions",
                "lots",
                "cancellations",
                "complaints",
                "contracts",
                "profile",
                "shortlistedFirms"
            )
        )
        _view_role = _view_tendering_role + whitelist("bids", "numberOfBids")
        _all_forbidden = whitelist()
        roles = {
            "create": _core_roles["create"] + _edit_role + whitelist("lots"),
            "edit": _edit_role,
            "edit_draft": _edit_role,
            "edit_draft.unsuccessful": _edit_role,
            "edit_draft.publishing": _all_forbidden,
            "edit_active.tendering": _all_forbidden,
            "edit_active.qualification": _all_forbidden,
            "edit_active.awarded": _all_forbidden,
            "edit_complete": _all_forbidden,
            "edit_unsuccessful": _all_forbidden,
            "edit_cancelled": _all_forbidden,
            "draft": _view_tendering_role,
            "draft.unsuccessful": _view_tendering_role,
            "draft.publishing": _view_tendering_role,
            "active.tendering": _view_tendering_role,
            "view": _view_role,
            "active.qualification": _view_role,
            "active.awarded": _view_role,
            "complete": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "chronograph": _core_roles["chronograph"],
            "chronograph_view": _core_roles["chronograph_view"],
            "Administrator": _core_roles["Administrator"],
            "plain": _core_roles["plain"],
            "listing": _core_roles["listing"],
            "contracting": _core_roles["contracting"],
            "default": _core_roles["default"],
            "bots": _edit_pq_bot_role,
        }

    status = StringType(choices=["draft",
                                 "draft.publishing",
                                 "draft.unsuccessful",
                                 "active.tendering",
                                 "active.qualification",
                                 "active.awarded",
                                 "complete",
                                 "cancelled",
                                 "unsuccessful"],
                        default="draft")

    # The goods and services to be purchased,
    # broken into line items wherever possible.
    # Items should not be duplicated, but a quantity of 2 specified instead.
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq,],
    )
    # The total estimated value of the procurement.
    value = ModelType(Value, required=True)
    # The period when the tender is open for submissions.
    # The end date is the closing date for tender submissions.
    tenderPeriod = ModelType(
        PeriodEndRequired, required=True
    )
    # The date or period on which an award is anticipated to be made.
    awardPeriod = ModelType(Period)
    # The number of unique tenderers who participated in the tender
    numberOfBidders = IntType()
    # A list of all the companies who entered submissions for the tender.
    bids = ListType(
        ModelType(Bid, required=True), default=list()
    )
    # The entity managing the procurement,
    # which may be different from the buyer
    # who is paying / using the items being procured.
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )
    awards = ListType(ModelType(Award, required=True), default=list())
    contracts = ListType(ModelType(Contract, required=True), default=list())
    minimalStep = ModelType(Value, required=True)
    questions = ListType(ModelType(Question, required=True), default=list())
    complaints = ListType(
        ComplaintModelType(Complaint, required=True),
        default=list()
    )
    cancellations = ListType(
        ModelType(Cancellation, required=True),
        default=list()
    )
    features = ListType(
        ModelType(Feature, required=True),
        validators=[validate_features_uniq]
    )
    lots = ListType(
        ModelType(Lot, required=True),
        default=list(),
        validators=[validate_lots_uniq]
    )
    guarantee = ModelType(Guarantee)
    procurementMethodType = StringType(default=PMT)
    profile = StringType()
    shortlistedFirms = ListType(ModelType(ShortlistedFirm), default=list())

    procuring_entity_kinds = ["general", "special",
                              "defense", "central", "other"]
    block_complaint_status = ["answered", "pending"]

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role in ("Administrator", "chronograph", "contracting", "bots"):
            role = request.authenticated_role
        elif request.authenticated_role == "auction":
            role = "auction_{}".format(request.method.lower())
        else:
            role = "edit_{}".format(request.context.status)
        return role

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == "active.tendering" and self.tenderPeriod.endDate:
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif (
            not self.lots
            and self.status == "active.awarded"
            and not any([
                i.status in self.block_complaint_status
                for i in self.complaints
            ])
            and not any([
                i.status in self.block_complaint_status
                for a in self.awards for i in a.complaints
            ])
        ):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards if a.complaintPeriod.endDate
            ]
            last_award_status = self.awards[-1].status if self.awards else ""
            if standStillEnds and last_award_status == "unsuccessful":
                checks.append(max(standStillEnds))
        elif (
            self.lots
            and self.status in ["active.qualification", "active.awarded"]
            and not any([
                i.status in self.block_complaint_status
                and i.relatedLot is None
                for i in self.complaints
            ])
        ):
            for lot in self.lots:
                if lot["status"] != "active":
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                pending_complaints = any(
                    [
                        i["status"] in self.block_complaint_status
                        and i.relatedLot == lot.id for i in self.complaints
                    ]
                )
                pending_awards_complaints = any(
                    [
                        i.status in self.block_complaint_status
                        for a in lot_awards for i in a.complaints
                    ]
                )
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards if a.complaintPeriod.endDate
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
                    checks.append(
                        calculate_tender_business_date(
                            complaint.dateAnswered,
                            COMPLAINT_STAND_STILL_TIME,
                            self
                        )
                    )
                elif complaint.status == "pending":
                    checks.append(self.dateModified)
            for award in self.awards:
                if award.status == "active" and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)
                for complaint in award.complaints:
                    if complaint.status == "answered" and complaint.dateAnswered:
                        checks.append(
                            calculate_tender_business_date(
                                complaint.dateAnswered,
                                COMPLAINT_STAND_STILL_TIME,
                                self)
                        )
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

    @serializable(serialized_name="guarantee",
                  serialize_when_none=False,
                  type=ModelType(Guarantee))
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [
                i.guarantee.amount for i in self.lots
                if i.guarantee
            ]
            if not lots_amount:
                return self.guarantee
            guarantee = {"amount": sum(lots_amount)}
            lots_currency = [
                i.guarantee.currency for i in self.lots
                if i.guarantee
            ]
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
        if data["status"] in ("draft", "draft.publishing", "draft.unsuccessful"):
            return
        cpv_336_group = items[0].classification.id[:3] == "336"\
            if items else False
        if (
            not cpv_336_group
            and (data.get("revisions")[0].date if data.get("revisions") else get_now()) > CPV_ITEMS_CLASS_FROM
            and items
            and len(set([i.classification.id[:4] for i in items])) != 1
        ):
            raise ValidationError(u"CPV class of items should be identical")
        else:
            validate_cpv_group(items)
        validate_classification_id(items)

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

    def validate_minimalStep(self, data, value):
        validate_minimalstep(data, value)

    def validate_awardPeriod(self, data, period):
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
