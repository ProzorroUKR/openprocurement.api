# -*- coding: utf-8 -*-
from openprocurement.tender.cfaselectionua.interfaces import ICFASelectionUATender
from openprocurement.tender.cfaselectionua.models.submodels.agreement import Agreement
from openprocurement.tender.cfaselectionua.models.submodels.award import Award
from openprocurement.tender.cfaselectionua.models.submodels.bid import Bid
from openprocurement.tender.cfaselectionua.models.submodels.contract import Contract
from openprocurement.tender.cfaselectionua.models.submodels.feature import Feature
from openprocurement.tender.cfaselectionua.models.submodels.item import Item
from openprocurement.tender.cfaselectionua.models.submodels.lot import Lot
from openprocurement.tender.cfaselectionua.models.submodels.organizationAndPocuringEntity import ProcuringEntity
from openprocurement.tender.cfaselectionua.constants import TENDERING_DURATION
from schematics.types import StringType, IntType, URLType, BooleanType
from schematics.types.compound import ModelType
from schematics.transforms import whitelist
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from zope.interface import implementer
from pyramid.security import Allow
from openprocurement.api.models import ListType, Period, Value, Guarantee
from openprocurement.api.validation import validate_items_uniq, validate_cpv_group
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ
from openprocurement.tender.core.models import (
    validate_lots_uniq,
    TenderAuctionPeriod,
    PeriodEndRequired,
    Tender as BaseTender,
    Cancellation as BaseCancellation,
    validate_features_uniq,
    validate_item_related_buyers,
)
from openprocurement.tender.core.utils import calc_auction_end_time, validate_features_custom_weight
from openprocurement.tender.core.validation import validate_minimalstep, validate_tender_period_duration
from decimal import Decimal


class Cancellation(BaseCancellation):
    _before_release_reasonType_choices = []

    _after_release_status_choices = ["draft", "unsuccessful", "active"]


@implementer(ICFASelectionUATender)
class CFASelectionUATender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    class Options:
        namespace = "Tender"
        _core_roles = BaseTender.Options.roles
        _not_implemented = whitelist("mainProcurementCategory", "milestones")
        _base_edit = (
            _core_roles["edit"]
            - _not_implemented
            + whitelist(
                "procuringEntity",
                "numberOfBidders",
                "guarantee",
                "items",
                "next_check",
                "tender_guarantee",
                "numberOfBids",
                "agreements",
                "hasEnquiries",
            )
        )
        _edit_role = _base_edit + whitelist(
            "enquiryPeriod", "tender_minimalStep", "contracts", "tenderPeriod", "features", "minimalStep"
        )
        _draft_view_role = (
            _core_roles["view"]
            - _not_implemented
            + whitelist(
                "tender_guarantee",
                "awardPeriod",
                "auctionUrl",
                "auctionPeriod",
                "next_check",
                "procuringEntity",
                "questions",
                "complaints",
                "lots",
                "items",
                "cancellations",
                "contracts",
                "agreements",
                "numberOfBidders",
                "awards",
                "guarantee",
                "hasEnquiries",
            )
        )
        _view_tendering_role = _draft_view_role + whitelist(
            "tender_value",
            "tenderPeriod",
            "features",
            "enquiryPeriod",
            "tender_minimalStep",
            "value",
            "minimalStep",
        )
        _view_role = _view_tendering_role + whitelist("bids", "numberOfBids")
        _procurement_method_details = whitelist("procurementMethodDetails")
        roles = {
            "create": _base_edit + whitelist("lots", "procurementMethodType", "mode"),
            "edit_draft": _core_roles["edit_draft"] + _procurement_method_details,
            "edit_draft.pending": whitelist("agreements", "unsuccessfulReason") + _procurement_method_details,
            "edit_cancelled": _procurement_method_details,
            "edit_complete": _procurement_method_details,
            "edit_unsuccessful": _procurement_method_details,
            "edit_active.awarded": _procurement_method_details,
            "edit_active.auction": _procurement_method_details,
            "edit_active.tendering": _procurement_method_details,
            "edit_active.qualification": _procurement_method_details,
            "edit_active.enquiries": whitelist(
                "description",
                "description_en",
                "description_ru",
                "documents",
                "items",
                "lots",
                "procurementMethodDetails",
                "guarantee",
                "tenderPeriod",
                "tender_guarantee",
                "title",
                "title_en",
                "title_ru",
            ),
            "edit": _edit_role,
            "edit_agreement_selection": whitelist("agreements", "procurementMethodDetails", "status"),
            "active.tendering": _view_tendering_role,
            "active.enquiries": _view_tendering_role,
            "active.auction": _view_tendering_role,
            "draft": _draft_view_role,
            "draft.pending": _draft_view_role + whitelist("features"),
            "draft.unsuccessful": _draft_view_role + whitelist("features", "unsuccessfulReason"),
            "active.awarded": _view_role,
            "unsuccessful": _view_role,
            "cancelled": _view_role,
            "view": _view_role,
            "active.qualification": _view_role,
            "complete": _view_role,
            "chronograph": _core_roles["chronograph"] + _procurement_method_details,
            "chronograph_view": _core_roles["chronograph_view"] + whitelist("agreements") + _procurement_method_details,
            "Administrator": _core_roles["Administrator"] + _procurement_method_details,
            "contracting": _core_roles["contracting"] + _procurement_method_details,
            "auction_post": _core_roles["auction_post"] + _procurement_method_details,
            "auction_patch": _core_roles["auction_patch"] + _procurement_method_details,
            "auction_view": _core_roles["auction_view"]
            + whitelist("minimalStep")
            + whitelist("tender_minimalStep")
            + _procurement_method_details,
            "listing": _core_roles["listing"] + _procurement_method_details,
            "embedded": _core_roles["embedded"],
            "plain": _core_roles["plain"],
            "default": _core_roles["default"],
        }

    items = ListType(
        ModelType(Item, required=True), min_size=1, validators=[validate_items_uniq]
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    value = ModelType(Value)  # The total estimated value of the procurement.
    enquiryPeriod = ModelType(
        PeriodEndRequired, required=False
    )  # The period during which enquiries may be made and will be answered.
    tenderPeriod = ModelType(
        PeriodEndRequired, required=False
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
    minimalStep = ModelType(Value)
    auctionUrl = URLType()
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    lots = ListType(
        ModelType(Lot, required=True), default=list(), validators=[validate_lots_uniq], min_size=1, max_size=1
    )
    guarantee = ModelType(Guarantee)
    status = StringType(
        choices=[
            "draft",
            "draft.pending",
            "draft.unsuccessful",
            "active.enquiries",
            "active.tendering",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="draft",
    )  # TODO Refactoring status
    agreements = ListType(ModelType(Agreement, required=True), default=list(), min_size=1, max_size=1)

    procurementMethod = StringType(choices=["open", "selective", "limited"], default="selective")
    procurementMethodType = StringType(default="closeFrameworkAgreementSelectionUA")
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    procuring_entity_kinds = ["authority", "central", "defense", "general", "other", "social", "special"]

    def get_role(self):
        root = self.__parent__
        request = root.request
        if request.authenticated_role == "Administrator":
            role = "Administrator"
        elif request.authenticated_role == "chronograph":
            role = "chronograph"
        elif request.authenticated_role == "auction":
            role = "auction_{}".format(request.method.lower())
        elif request.authenticated_role == "contracting":
            role = "contracting"
        elif request.authenticated_role == "agreement_selection":
            role = "edit_{}".format(request.authenticated_role)
        else:
            role = "edit_{}".format(request.context.status)
        return role

    def __acl__(self):
        acl = [(Allow, "{}_{}".format(i.owner, i.owner_token), "create_award_complaint") for i in self.bids]
        acl.extend(
            [
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_complaint"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "edit_contract"),
                (Allow, "{}_{}".format(self.owner, self.owner_token), "upload_contract_documents"),
                (Allow, "g:agreement_selection", "edit_agreement_selection"),
                (Allow, "g:agreement_selection", "edit_tender"),
                (Allow, "g:brokers", "create_cancellation_complaint")
            ]
        )
        self._acl_cancellation(acl)
        return acl

    def __local_roles__(self):
        roles = dict([("{}_{}".format(self.owner, self.owner_token), "tender_owner")])
        for i in self.bids:
            roles["{}_{}".format(i.owner, i.owner_token)] = "bid_owner"
        return roles

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        pass

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def tender_guarantee(self):
        return self.guarantee
        # if self.lots:
        #     lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
        #     if not lots_amount:
        #         return self.guarantee
        #     guarantee = {"amount": sum(lots_amount)}
        #     lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
        #     guarantee["currency"] = lots_currency[0] if lots_currency else None
        #     if self.guarantee:
        #         guarantee["currency"] = self.guarantee.currency
        #     guarantee_class = self._fields["guarantee"]
        #     return guarantee_class(guarantee)
        # else:
        #     return self.guarantee

    @serializable(serialized_name="minimalStep", serialize_when_none=False, type=ModelType(Value, required=False))
    def tender_minimalStep(self):
        return self.minimalStep
        # if all([i.minimalStep for i in self.lots]):
        #     value_class = self._fields["minimalStep"]
        #     return (
        #         value_class(
        #             dict(
        #                 amount=min([i.minimalStep.amount for i in self.lots]),
        #                 currency=self.lots[0].minimalStep.currency,
        #                 valueAddedTaxIncluded=self.lots[0].minimalStep.valueAddedTaxIncluded,
        #             )
        #         )
        #         if self.lots
        #         else self.minimalStep
        #     )

    @serializable(serialized_name="value", serialize_when_none=False, type=ModelType(Value))
    def tender_value(self):
        return self.value
        # if all([i.value for i in self.lots]):
        #     value_class = self._fields["value"]
        #     return (
        #         value_class(
        #             dict(
        #                 amount=sum([i.value.amount for i in self.lots]),
        #                 currency=self.lots[0].value.currency,
        #                 valueAddedTaxIncluded=self.lots[0].value.valueAddedTaxIncluded,
        #             )
        #         )
        #         if self.lots
        #         else self.value
        #     )

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == "active.enquiries" and self.enquiryPeriod and self.enquiryPeriod.endDate:
            checks.append(self.enquiryPeriod.endDate.astimezone(TZ))
        elif self.status == "active.tendering" and self.tenderPeriod and self.tenderPeriod.endDate:
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
        elif self.lots and self.status in ["active.qualification", "active.awarded"]:
            for lot in self.lots:
                if lot["status"] != "active":
                    continue
        if self.status.startswith("active"):
            for award in self.awards:
                if award.status == "active" and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)
        return min(checks).isoformat() if checks else None

    @serializable
    def numberOfBids(self):
        return len(self.bids)

    def validate_auctionUrl(self, data, url):
        if url and data["lots"]:
            raise ValidationError("url should be posted for each lot")

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("auctionPeriod")
            and data.get("auctionPeriod").endDate
            and period.startDate < data.get("auctionPeriod").endDate
        ):
            raise ValidationError("period should begin after auctionPeriod")
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError("period should begin after tenderPeriod")

    def validate_features(self, data, features):
        validate_features_custom_weight(data, features, Decimal("0.3"))

    def validate_items(self, data, items):
        cpv_336_group = items[0].classification.id[:3] == "336" if items else False
        if not cpv_336_group and items and len(set([i.classification.id[:4] for i in items])) != 1:
            raise ValidationError("CPV class of items should be identical")
        else:
            validate_cpv_group(items)
        validate_item_related_buyers(data, items)

    def validate_lots(self, data, lots):
        if len(set([lot.guarantee.currency for lot in lots if lot.guarantee])) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")

    def validate_minimalStep(self, data, value):
        validate_minimalstep(data, value)

    def validate_tenderPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("enquiryPeriod")
            and data.get("enquiryPeriod").endDate
            and period.startDate < data.get("enquiryPeriod").endDate
        ):
            raise ValidationError("period should begin after enquiryPeriod")
        if (
            period
            and period.startDate
            and period.endDate
        ):
            validate_tender_period_duration(data, period, TENDERING_DURATION)
